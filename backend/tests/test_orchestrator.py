import pytest

from app.challenges.registry import load_challenges
from app.progress.service import completed_ids
from app.sql.orchestrator import submit
from app.sql.sandbox import review_sandbox_factory
from tests.helpers import PROTOTYPE_DIR, internal_state, visible_state

CHALLENGES = load_challenges(PROTOTYPE_DIR).all()
FIRST = CHALLENGES[0]


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


def test_pass_records_progress_once(conn, store):
    sandbox = review_sandbox_factory(store.template_path, CHALLENGES, FIRST.id)
    first = submit(conn, FIRST, FIRST.reference_sql)
    again = submit(conn, FIRST, "select email as e, last_name, first_name from customers", review_sandbox=sandbox)
    third = submit(conn, FIRST, FIRST.accepted_alternatives[0], review_sandbox=sandbox)

    assert first.passed and first.newly_completed and not first.review_mode
    assert again.code == "column_order"
    assert third.passed and not third.newly_completed and third.review_mode and not third.persisted
    assert completed_ids(conn) == {FIRST.id}
    assert not conn.in_transaction


def test_completed_query_without_sandbox_is_an_error(conn):
    submit(conn, FIRST, FIRST.reference_sql)
    with pytest.raises(RuntimeError):
        submit(conn, FIRST, FIRST.reference_sql)


def test_completed_query_is_replayed_against_its_historical_state(store, conn):
    """Later changes to the live database must not break an earlier completed query."""
    submit(conn, FIRST, FIRST.reference_sql)
    conn.execute("UPDATE customers SET email = 'changed@example.com' WHERE customer_id = 1")
    sandbox = review_sandbox_factory(store.template_path, CHALLENGES, FIRST.id)

    outcome = submit(conn, FIRST, FIRST.reference_sql, review_sandbox=sandbox)

    assert outcome.passed and outcome.review_mode
    assert ("changed@example.com",) not in [(row[2],) for row in outcome.result.rows]
    assert conn.execute("SELECT email FROM customers WHERE customer_id = 1").fetchone() == ("changed@example.com",)
