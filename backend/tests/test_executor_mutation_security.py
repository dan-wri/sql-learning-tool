"""Security tests for learner SQL under an INSERT-only policy on customers."""

import pytest

from app.sql.authorizer import AccessPolicy
from app.sql.executor import MAX_CHANGES, QueryError, execute_learner_sql
from tests.helpers import internal_state, visible_state

INSERT_CUSTOMERS = AccessPolicy(write_operations=frozenset(
    {"INSERT"}), writable_tables=frozenset({"customers"}))
MISCONFIGURED = AccessPolicy(
    write_operations=frozenset({"INSERT", "UPDATE", "DELETE"}),
    writable_tables=frozenset(
        {"customers", "_app_progress", "_app_hints", "_app_meta", "sqlite_schema"}),
)

NEW_CUSTOMER = (
    "INSERT INTO customers (first_name, last_name, email, city, country, signup_date) "
    "VALUES ('Ada', 'Lovelace', 'ada@example.com', 'London', 'UK', '2025-07-01')"
)


@pytest.fixture
def conn(store, learner_id):
    with store.connection(learner_id) as connection:
        connection.execute("BEGIN IMMEDIATE")
        yield connection
        if connection.in_transaction:
            connection.execute("ROLLBACK")


def assert_rejected(conn, sql, kind, policy=INSERT_CUSTOMERS, **kwargs):
    before = visible_state(conn), internal_state(conn)
    with pytest.raises(QueryError) as excinfo:
        execute_learner_sql(conn, sql, policy, **kwargs)
    assert excinfo.value.kind == kind, excinfo.value.message
    # The learner can never end the transaction the app opened.
    assert conn.in_transaction or kind == "timeout"
    if conn.in_transaction:
        assert (visible_state(conn), internal_state(conn)) == before
    return excinfo.value


@pytest.mark.parametrize(
    "sql",
    [
        NEW_CUSTOMER,
        NEW_CUSTOMER + " RETURNING customer_id",
        "WITH v AS (SELECT 'Ada' AS f) INSERT INTO customers (first_name, last_name, email, city, country, "
        "signup_date) SELECT f, 'Lovelace', 'ada@example.com', 'London', 'UK', '2025-07-01' FROM v",
    ],
)
def test_insert_into_allowed_table_is_permitted(conn, sql):
    before = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    execute_learner_sql(conn, sql, INSERT_CUSTOMERS)
    assert conn.execute(
        "SELECT COUNT(*) FROM customers").fetchone()[0] == before + 1
    assert conn.in_transaction


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE customers SET city = 'Paris'",
        "DELETE FROM customers WHERE customer_id = 60",
        NEW_CUSTOMER.replace(
            "'ada@example.com'", "(SELECT email FROM customers WHERE customer_id = 1)")
        + " ON CONFLICT (email) DO UPDATE SET city = 'Paris'",
        "INSERT INTO categories (name) VALUES ('Garden')",
        "INSERT INTO orders (customer_id, order_date, status) VALUES (1, '2025-07-01', 'pending')",
        "UPDATE products SET price = 0",
        "DELETE FROM payments",
    ],
)
def test_other_writes_are_rejected(conn, sql):
    assert_rejected(conn, sql, "not_allowed")


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO _app_progress VALUES ('premium-products', '2025-01-01')",
        "UPDATE _app_hints SET hints_revealed = 99",
        "DELETE FROM _app_progress",
        "INSERT INTO _app_meta VALUES ('x', 'y')",
        "SELECT * FROM _app_progress",
        NEW_CUSTOMER.replace(
            "'Ada'", "(SELECT challenge_id FROM _app_progress LIMIT 1)"),
    ],
)
def test_internal_tables_stay_hidden_even_if_configured_writable(conn, sql):
    error = assert_rejected(conn, sql, "not_allowed", policy=MISCONFIGURED)
    assert "_app_" not in error.message


@pytest.mark.parametrize(
    "sql",
    ["BEGIN", "COMMIT", "END", "ROLLBACK", "SAVEPOINT s", "RELEASE s", "ROLLBACK TO s",
     "BEGIN IMMEDIATE TRANSACTION", "COMMIT TRANSACTION"],
)
def test_transaction_control_is_rejected(conn, sql):
    assert_rejected(conn, sql, "not_allowed")


def test_learner_cannot_commit_their_insert(conn):
    assert_rejected(conn, NEW_CUSTOMER + "; COMMIT", "multiple_statements")
    assert_rejected(conn, "COMMIT; " + NEW_CUSTOMER, "not_allowed")


@pytest.mark.parametrize(
    "sql",
    [
        "CREATE TABLE evil (id INTEGER)",
        "DROP TABLE customers",
        "ALTER TABLE customers ADD COLUMN evil TEXT",
        "CREATE TRIGGER evil AFTER INSERT ON customers BEGIN DELETE FROM orders; END",
        "CREATE INDEX idx_evil ON customers (email)",
        "PRAGMA foreign_keys = OFF",
        "ATTACH DATABASE '/tmp/evil.db' AS evil",
        "VACUUM INTO '/tmp/evil.db'",
        "REINDEX",
        "ANALYZE",
        "EXPLAIN " + NEW_CUSTOMER,
        "SELECT load_extension('/tmp/evil')",
    ],
)
def test_previously_blocked_operations_stay_blocked(conn, sql):
    assert_rejected(conn, sql, "not_allowed")


def test_mass_insert_is_capped(conn):
    sql = (
        "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r WHERE n < {limit}) "
        "INSERT INTO customers (first_name, last_name, email, city, country, signup_date) "
        "SELECT 'x', 'y', 'bulk' || n || '@example.com', 'z', 'z', '2025-01-01' FROM r"
    ).format(limit=MAX_CHANGES + 1)
    assert_rejected(conn, sql, "too_many_changes")


def test_runaway_insert_times_out(conn):
    sql = (
        "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r) "
        "INSERT INTO customers (first_name, last_name, email, city, country, signup_date) "
        "SELECT 'x', 'y', 'e@example.com', 'z', 'z', '2025-01-01' FROM r WHERE n < 0"
    )
    assert_rejected(conn, sql, "timeout", timeout_seconds=0.2)


def test_constraint_violation_is_reported(conn):
    error = assert_rejected(
        conn, "INSERT INTO customers (first_name, last_name, email) VALUES ('a', 'b', 'c@example.com')", "sql_error")
    assert "NOT NULL" in error.message


def test_learner_sql_refuses_to_run_outside_a_transaction(store, learner_id):
    with store.connection(learner_id) as connection:
        with pytest.raises(RuntimeError):
            execute_learner_sql(connection, NEW_CUSTOMER, INSERT_CUSTOMERS)
        assert connection.execute(
            "SELECT COUNT(*) FROM customers WHERE email = 'ada@example.com'").fetchone()[0] == 0
