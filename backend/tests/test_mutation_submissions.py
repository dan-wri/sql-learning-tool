import pytest

from app.challenges.registry import load_challenges
from app.config import CHALLENGES_DIR
from app.progress.service import completed_ids
from app.sql.orchestrator import submit
from app.sql.sandbox import canonical_state_before, review_sandbox_factory
from tests.helpers import internal_state, replay_until, visible_state

CHALLENGES = load_challenges(CHALLENGES_DIR).all()
INSERT_CHALLENGE = next(c for c in CHALLENGES if c.id == "add-new-customer")

COLUMNS = "(first_name, last_name, email, city, country, signup_date)"
GOOD_VALUES = "('Grace', 'Hopper', 'grace.hopper@example.com', 'London', 'UK', '2025-07-01')"
GRACE_COUNT = "SELECT COUNT(*) FROM customers WHERE email = 'grace.hopper@example.com'"


@pytest.fixture
def conn(store, learner_id):
    with store.connection(learner_id) as connection:
        replay_until(connection, CHALLENGES, INSERT_CHALLENGE.id)
        yield connection


def state(conn):
    return visible_state(conn), internal_state(conn)


FAILURES = [
    (f"INSERT INTO customers {COLUMNS} VALUES ('Grace', 'Hopper', 'grace@example.com', 'London', 'UK', '2025-07-01')",
     "wrong_values", "Check: email"),
    (f"INSERT INTO customers (customer_id, {COLUMNS[1:]} VALUES (100, {GOOD_VALUES[1:]}",
     "wrong_values", "Check: customer_id"),
    (f"INSERT INTO customers {COLUMNS} VALUES {GOOD_VALUES}, "
     "('Alan', 'Turing', 'alan@example.com', 'London', 'UK', '2025-07-01')",
     "row_count", "Your INSERT created 2 rows in customers; this task expects 1."),
    (f"INSERT INTO customers {COLUMNS} SELECT 'Grace', 'Hopper', 'g@example.com', 'London', 'UK', '2025-07-01' "
     "WHERE 1 = 0",
     "row_count", "Your INSERT created 0 rows in customers; this task expects 1."),
    ("SELECT * FROM customers", "wrong_statement", "This challenge requires an INSERT statement."),
    ("UPDATE customers SET city = 'London' WHERE customer_id = 1", "not_allowed", "UPDATE isn't allowed"),
    ("DELETE FROM customers WHERE customer_id = 60", "not_allowed", "DELETE isn't allowed"),
    ("INSERT INTO categories (name) VALUES ('Garden')", "not_allowed", "categories can't be modified"),
    ("INSERT INTO customers (first_name, last_name, email) VALUES ('Grace', 'Hopper', 'g@example.com')",
     "sql_error", "NOT NULL"),
    (f"INSERT INTO customers {COLUMNS} SELECT 'Grace', 'Hopper', email, 'London', 'UK', '2025-07-01' "
     "FROM customers WHERE customer_id = 1",
     "sql_error", "UNIQUE"),
    ("COMMIT", "not_allowed", "Transactions are managed for you"),
    (f"INSERT INTO customers {COLUMNS} VALUES {GOOD_VALUES}; COMMIT", "multiple_statements", "one SQL statement"),
]


@pytest.mark.parametrize("sql, code, fragment", FAILURES)
def test_failed_mutation_rolls_back_everything(conn, sql, code, fragment):
    before = state(conn)
    outcome = submit(conn, INSERT_CHALLENGE, sql)

    assert not outcome.passed
    assert outcome.code == code
    assert fragment in outcome.message
    assert not outcome.persisted
    assert state(conn) == before
    assert INSERT_CHALLENGE.id not in completed_ids(conn)
    assert not conn.in_transaction


def test_failed_mutation_previews_the_learners_own_changes(conn):
    sql = f"INSERT INTO customers {COLUMNS} VALUES ('Grace', 'Hopper', 'oops@example.com', 'London', 'UK', '2025-07-01')"
    outcome = submit(conn, INSERT_CHALLENGE, sql)

    assert list(outcome.changes) == ["customers"]
    (row,) = outcome.changes["customers"].inserted
    assert row[3] == "oops@example.com"
    assert conn.execute("SELECT COUNT(*) FROM customers WHERE email = 'oops@example.com'").fetchone()[0] == 0


def test_timeout_rolls_back(conn):
    before = state(conn)
    sql = (f"WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r) INSERT INTO customers {COLUMNS} "
           "SELECT 'Grace', 'Hopper', 'grace.hopper@example.com', 'London', 'UK', '2025-07-01' FROM r WHERE n < 0")
    outcome = submit(conn, INSERT_CHALLENGE, sql, timeout_seconds=0.2)
    assert outcome.code == "timeout"
    assert state(conn) == before
    assert not conn.in_transaction


@pytest.mark.parametrize("sql", [INSERT_CHALLENGE.reference_sql, *INSERT_CHALLENGE.accepted_alternatives])
def test_correct_insert_commits_data_and_progress_together(conn, sql):
    outcome = submit(conn, INSERT_CHALLENGE, sql)

    assert outcome.passed, outcome.message
    assert outcome.persisted and outcome.newly_completed and not outcome.review_mode
    assert conn.execute(GRACE_COUNT).fetchone()[0] == 1
    assert INSERT_CHALLENGE.id in completed_ids(conn)
    assert not conn.in_transaction


def test_review_mode_validates_but_never_persists(store, conn):
    submit(conn, INSERT_CHALLENGE, INSERT_CHALLENGE.reference_sql)
    after_first_pass = state(conn)
    sandbox = review_sandbox_factory(store.template_path, CHALLENGES, INSERT_CHALLENGE.id)

    replay = submit(conn, INSERT_CHALLENGE, INSERT_CHALLENGE.accepted_alternatives[1], review_sandbox=sandbox)
    assert replay.passed and replay.review_mode, replay.message
    assert not replay.persisted and not replay.newly_completed
    assert replay.changes["customers"].inserted
    assert state(conn) == after_first_pass

    wrong = submit(conn, INSERT_CHALLENGE, f"INSERT INTO customers {COLUMNS} VALUES "
                                           "('Grace', 'Hopper', 'gh@example.com', 'Leeds', 'UK', '2025-07-01')",
                   review_sandbox=sandbox)
    assert not wrong.passed and wrong.review_mode
    assert wrong.code == "wrong_values"
    assert "Check: email, city" in wrong.message

    blocked = submit(conn, INSERT_CHALLENGE, "DELETE FROM customers", review_sandbox=sandbox)
    assert blocked.code == "not_allowed" and blocked.review_mode

    assert state(conn) == after_first_pass
    assert conn.execute(GRACE_COUNT).fetchone()[0] == 1


def test_review_sandbox_matches_learner_state_before_the_challenge(store, conn):
    before_challenge = visible_state(conn)
    sandbox = canonical_state_before(store.template_path, CHALLENGES, INSERT_CHALLENGE.id)
    try:
        assert visible_state(sandbox) == before_challenge
    finally:
        sandbox.close()
