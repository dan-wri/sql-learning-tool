"""Run learner SQL against a learner database with guards on what it can do and how long it can run.

The caller owns the transaction; this module never begins, commits or rolls back.
"""

import re
import sqlite3
import time
from dataclasses import dataclass

from app.sql.authorizer import MSG_TRANSACTION, READ_ONLY, AccessPolicy, Authorizer

MAX_SQL_LENGTH = 5_000
MAX_ROWS = 500
MAX_CHANGES = 1_000
TIMEOUT_SECONDS = 2.0
PROGRESS_INTERVAL = 1_000

READ_KEYWORDS = {"SELECT", "WITH", "VALUES"}
WRITE_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "REPLACE"}
TRANSACTION_KEYWORDS = {"BEGIN", "COMMIT",
                        "END", "ROLLBACK", "SAVEPOINT", "RELEASE"}
STATEMENT_KEYWORDS = READ_KEYWORDS | WRITE_KEYWORDS | {
    "ALTER", "ANALYZE", "ATTACH", "BEGIN", "COMMIT", "CREATE", "DETACH", "DROP", "END", "EXPLAIN",
    "PRAGMA", "REINDEX", "RELEASE", "ROLLBACK", "SAVEPOINT", "VACUUM",
}

_LEADING_NOISE = re.compile(
    r"\A(?:\s+|--[^\n]*(?:\n|\Z)|/\*.*?(?:\*/|\Z))*", re.DOTALL)
_FIRST_WORD = re.compile(r"[A-Za-z]+")


class QueryError(Exception):
    """A learner-facing failure. kind is one of: empty, too_long, multiple_statements, not_allowed, timeout,
    too_many_changes, sql_error."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind
        self.message = message


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[tuple]
    truncated: bool


def first_keyword(sql: str) -> str | None:
    rest = _LEADING_NOISE.sub("", sql, count=1)
    match = _FIRST_WORD.match(rest)
    return match.group(0).upper() if match else None


def _check_text(sql: str, policy: AccessPolicy) -> None:
    if len(sql) > MAX_SQL_LENGTH:
        raise QueryError(
            "too_long", f"Your query is too long (limit is {MAX_SQL_LENGTH:,} characters).")
    stripped = _LEADING_NOISE.sub("", sql, count=1).strip().strip(";").strip()
    if not stripped:
        raise QueryError("empty", "Write a query before submitting.")
    allowed = READ_KEYWORDS if policy.read_only else READ_KEYWORDS | WRITE_KEYWORDS
    keyword = first_keyword(sql)
    # Unknown first words (typos) fall through so SQLite reports a syntax error; the authorizer still applies.
    if keyword in STATEMENT_KEYWORDS - allowed:
        if keyword in TRANSACTION_KEYWORDS:
            raise QueryError("not_allowed", MSG_TRANSACTION)
        message = "Only SELECT queries are allowed in this challenge." if policy.read_only else (
            f"Only {' and '.join(sorted(policy.write_operations))} statements are allowed in this challenge.")
        raise QueryError("not_allowed", message)


def _run(conn: sqlite3.Connection, sql: str, max_rows: int | None, timeout_seconds: float,
         authorizer: Authorizer | None, max_changes: int | None = None) -> QueryResult:
    deadline = time.monotonic() + timeout_seconds
    timed_out = False
    changes_before = conn.total_changes

    def progress() -> int:
        nonlocal timed_out
        timed_out = time.monotonic() > deadline
        return 1 if timed_out else 0

    conn.set_progress_handler(progress, PROGRESS_INTERVAL)
    if authorizer is not None:
        conn.set_authorizer(authorizer)
    try:
        cursor = conn.execute(sql)
        columns = [d[0]
                   for d in cursor.description] if cursor.description else []
        if max_rows is None:
            rows, truncated = cursor.fetchall(), False
        else:
            rows = cursor.fetchmany(max_rows + 1)
            truncated = len(rows) > max_rows
            rows = rows[:max_rows]
        cursor.close()
        if max_changes is not None and conn.total_changes - changes_before > max_changes:
            raise QueryError("too_many_changes",
                             f"Your statement changed more than {max_changes:,} rows, far more than this task needs.")
        return QueryResult(columns=columns, rows=rows, truncated=truncated)
    except sqlite3.ProgrammingError as exc:
        if "one statement at a time" in str(exc):
            raise QueryError("multiple_statements",
                             "Submit one SQL statement at a time.") from None
        raise QueryError("sql_error", str(exc)) from None
    except sqlite3.Error as exc:
        if authorizer is not None and authorizer.denial:
            raise QueryError("not_allowed", authorizer.denial) from None
        if timed_out:
            raise QueryError(
                "timeout", f"Your query took longer than {timeout_seconds:g}s and was stopped.") from None
        raise QueryError("sql_error", str(exc)) from None
    finally:
        conn.set_progress_handler(None, 0)
        if authorizer is not None:
            conn.set_authorizer(None)


def execute_learner_sql(conn: sqlite3.Connection, sql: str, policy: AccessPolicy = READ_ONLY, *,
                        timeout_seconds: float = TIMEOUT_SECONDS, max_rows: int = MAX_ROWS) -> QueryResult:
    """On QueryError the statement's changes are undone; on success they stay in the caller's transaction."""
    if not conn.in_transaction:
        raise RuntimeError(
            "Learner SQL must run inside a transaction owned by the caller")
    _check_text(sql, policy)
    conn.execute("SAVEPOINT learner_statement")
    try:
        result = _run(conn, sql, max_rows, timeout_seconds,
                      Authorizer(policy), MAX_CHANGES)
    except QueryError:
        # An interrupt can make SQLite roll back the whole transaction by itself.
        if conn.in_transaction:
            conn.execute("ROLLBACK TO learner_statement")
            conn.execute("RELEASE learner_statement")
        raise
    conn.execute("RELEASE learner_statement")
    return result


def execute_trusted(conn: sqlite3.Connection, sql: str, *, timeout_seconds: float = TIMEOUT_SECONDS) -> QueryResult:
    """Run challenge-authored SQL (reference solutions). Still time-limited so bad content can't hang a request."""
    return _run(conn, sql, None, timeout_seconds, None)
