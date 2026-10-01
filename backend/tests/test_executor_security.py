"""Security tests for learner SQL under the read-only policy used by SELECT challenges."""

import pytest

from app.sql.executor import MAX_SQL_LENGTH, READ_ONLY, QueryError, execute_learner_sql
from tests.helpers import internal_state, visible_state


@pytest.fixture
def conn(store, learner_id):
    with store.connection(learner_id) as connection:
        yield connection


def run_in_transaction(conn, sql, **kwargs):
    conn.execute("BEGIN IMMEDIATE")
    try:
        return execute_learner_sql(conn, sql, READ_ONLY, **kwargs)
    finally:
        if conn.in_transaction:
            conn.execute("ROLLBACK")


def assert_rejected(conn, sql, kind):
    before = visible_state(conn), internal_state(conn)
    with pytest.raises(QueryError) as excinfo:
        run_in_transaction(conn, sql)
    assert excinfo.value.kind == kind, excinfo.value.message
    assert (visible_state(conn), internal_state(conn)) == before
    return excinfo.value


WRITES_AND_DDL = [
    "INSERT INTO customers (first_name, last_name, email, city, country, signup_date) "
    "VALUES ('a', 'b', 'c@example.com', 'x', 'y', '2025-01-01')",
    "UPDATE products SET price = 0",
    "DELETE FROM payments",
    "REPLACE INTO categories (category_id, name) VALUES (1, 'Hacked')",
    "WITH doomed AS (SELECT 1) DELETE FROM payments",
    "CREATE TABLE evil (id INTEGER)",
    "CREATE TEMP TABLE evil (id INTEGER)",
    "DROP TABLE customers",
    "ALTER TABLE customers ADD COLUMN evil TEXT",
    "CREATE INDEX idx_evil ON customers (email)",
    "CREATE VIEW evil AS SELECT * FROM customers",
    "CREATE TRIGGER evil AFTER INSERT ON customers BEGIN DELETE FROM orders; END",
    "PRAGMA foreign_keys = OFF",
    "PRAGMA table_info(customers)",
    "ATTACH DATABASE '/tmp/evil.db' AS evil",
    "DETACH DATABASE main",
    "VACUUM",
    "VACUUM INTO '/tmp/evil.db'",
    "REINDEX",
    "ANALYZE",
    "EXPLAIN DELETE FROM payments",
    "/* sneaky */ DROP TABLE customers",
    "-- comment\nDELETE FROM payments",
    "delete from payments",
]

TRANSACTION_CONTROL = ["BEGIN", "COMMIT", "END",
                       "ROLLBACK", "SAVEPOINT s", "RELEASE s", "ROLLBACK TO s"]

INTERNAL_TABLE_ACCESS = [
    "SELECT * FROM _app_progress",
    "SELECT COUNT(*) FROM _app_meta",
    "SELECT challenge_id FROM _APP_PROGRESS",
    'SELECT * FROM "_app_hints"',
    "SELECT * FROM main._app_progress",
    "SELECT c.first_name FROM customers c JOIN _app_progress p ON 1 = 1",
    "SELECT * FROM customers WHERE customer_id IN (SELECT 1 FROM _app_progress)",
    "WITH p AS (SELECT * FROM _app_progress) SELECT * FROM p",
    "SELECT name, sql FROM sqlite_schema",
    "SELECT name FROM sqlite_master",
    "SELECT * FROM pragma_table_info('customers')",
]


@pytest.mark.parametrize("sql", WRITES_AND_DDL)
def test_writes_and_ddl_are_rejected(conn, sql):
    assert_rejected(conn, sql, "not_allowed")


@pytest.mark.parametrize("sql", TRANSACTION_CONTROL)
def test_transaction_control_is_rejected(conn, sql):
    assert_rejected(conn, sql, "not_allowed")


@pytest.mark.parametrize("sql", INTERNAL_TABLE_ACCESS)
def test_internal_tables_are_hidden(conn, sql):
    error = assert_rejected(conn, sql, "not_allowed")
    assert "_app_" not in error.message


def test_load_extension_is_rejected(conn):
    assert_rejected(conn, "SELECT load_extension('/tmp/evil')", "not_allowed")


@pytest.mark.parametrize(
    "sql",
    ["SELECT 1; DROP TABLE customers", "SELECT 1; SELECT 2", "SELECT 1;; SELECT 2"],
)
def test_multiple_statements_are_rejected(conn, sql):
    assert_rejected(conn, sql, "multiple_statements")


@pytest.mark.parametrize("sql", ["", "   ", "-- just a comment", "/* nothing */"])
def test_empty_input_is_rejected(conn, sql):
    assert_rejected(conn, sql, "empty")


def test_overlong_input_is_rejected(conn):
    sql = "SELECT 1 " + " " * MAX_SQL_LENGTH
    assert_rejected(conn, sql, "too_long")


def test_syntax_errors_are_reported(conn):
    error = assert_rejected(conn, "SELEC * FROM customers", "sql_error")
    assert "syntax error" in error.message
    error = assert_rejected(conn, "SELECT * FORM customers", "sql_error")
    assert "syntax error" in error.message


def test_runaway_query_times_out(conn):
    sql = "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r) SELECT COUNT(*) FROM r"
    before = visible_state(conn), internal_state(conn)
    with pytest.raises(QueryError) as excinfo:
        run_in_transaction(conn, sql, timeout_seconds=0.2)
    assert excinfo.value.kind == "timeout"
    assert (visible_state(conn), internal_state(conn)) == before


def test_connection_is_usable_after_timeout(conn):
    with pytest.raises(QueryError):
        run_in_transaction(
            conn, "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r) SELECT COUNT(*) FROM r",
            timeout_seconds=0.1,
        )
    assert run_in_transaction(
        conn, "SELECT COUNT(*) FROM customers").rows[0][0] > 0


def test_result_rows_are_capped(conn):
    sql = "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r WHERE n < 5000) SELECT n FROM r"
    result = run_in_transaction(conn, sql, max_rows=100)
    assert len(result.rows) == 100
    assert result.truncated is True


def test_authorizer_is_removed_afterwards(conn):
    run_in_transaction(conn, "SELECT 1")
    assert conn.execute(
        "SELECT COUNT(*) FROM _app_progress").fetchone()[0] == 0


def test_previously_prepared_statement_cannot_bypass_authorizer(conn):
    sql = "SELECT COUNT(*) FROM _app_progress"
    conn.execute(sql).fetchall()
    assert_rejected(conn, sql, "not_allowed")


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT first_name, last_name FROM customers",
        "select * from products where price > 50 order by price desc limit 3;",
        "  SELECT 1 ; -- trailing comment",
        "VALUES (1, 2)",
        "WITH big AS (SELECT * FROM products WHERE price > 100) SELECT name FROM big",
        "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r WHERE n < 10) SELECT n FROM r",
        "SELECT UPPER(city), COUNT(*) FROM customers GROUP BY city",
        "SELECT * FROM customers WHERE email LIKE '%drop table%'",
    ],
)
def test_reads_are_allowed(conn, sql):
    result = run_in_transaction(conn, sql)
    assert result.columns
    assert result.truncated is False
