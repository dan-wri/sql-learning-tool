import pytest

from app.challenges.registry import load_challenges
from app.config import CHALLENGES_DIR
from app.progress.service import completed_ids
from app.sql.orchestrator import submit
from tests.helpers import internal_state, visible_state

FIRST = load_challenges(CHALLENGES_DIR).all()[0]


@pytest.fixture
def conn(store, learner_id):
    with store.connection(learner_id) as connection:
        yield connection


@pytest.mark.parametrize(
    "sql, code",
    [
        ("SELECT first_name, last_name FROM customers", "column_count"),
        ("SELECT first_name, last_name, email FROM customers LIMIT 5", "row_count"),
        ("SELECT first_name, last_name, phone FROM customers", "wrong_values"),
        ("DELETE FROM customers", "not_allowed"),
        ("SELECT * FROM _app_progress", "not_allowed"),
        ("SELECT nope FROM customers", "sql_error"),
    ],
)
def test_failed_submission_leaves_state_and_progress_unchanged(conn, sql, code):
    before = visible_state(conn), internal_state(conn)
    outcome = submit(conn, FIRST, sql)
    assert not outcome.passed
    assert outcome.code == code
    assert (visible_state(conn), internal_state(conn)) == before
    assert not conn.in_transaction


def test_timeout_rolls_back(conn):
    before = visible_state(conn), internal_state(conn)
    outcome = submit(
        conn, FIRST,
        "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r) SELECT n, n, n FROM r WHERE n < 0",
        timeout_seconds=0.2,
    )
    assert outcome.code == "timeout"
    assert (visible_state(conn), internal_state(conn)) == before
    assert not conn.in_transaction


def test_pass_records_progress_once(conn):
    first = submit(conn, FIRST, FIRST.reference_sql)
    again = submit(conn, FIRST, "select email as e, last_name, first_name from customers")
    third = submit(conn, FIRST, FIRST.accepted_alternatives[0])

    assert first.passed and first.newly_completed
    assert again.code == "column_order"
    assert third.passed and not third.newly_completed
    assert completed_ids(conn) == {FIRST.id}
    assert not conn.in_transaction
