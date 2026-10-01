"""One submission = one transaction on the learner's database.

Reference and learner SQL both start from the same state: the reference runs inside a
savepoint that is rolled back before the learner's SQL runs. The transaction commits only
on a pass, so a failed submission never changes data or progress.
"""

import sqlite3
from dataclasses import dataclass

from app.challenges.registry import Challenge
from app.progress.service import mark_completed
from app.sql.executor import TIMEOUT_SECONDS, QueryError, QueryResult, execute_learner_sql, execute_trusted
from app.validation.result_validator import Verdict, compare_results


@dataclass(frozen=True)
class SubmissionOutcome:
    passed: bool
    code: str
    message: str
    result: QueryResult | None
    newly_completed: bool


def _rollback(conn: sqlite3.Connection) -> None:
    # SQLite can already have rolled back by itself (e.g. after an interrupt).
    if conn.in_transaction:
        conn.execute("ROLLBACK")


def submit(conn: sqlite3.Connection, challenge: Challenge, sql: str, *,
           timeout_seconds: float = TIMEOUT_SECONDS) -> SubmissionOutcome:
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute("SAVEPOINT reference")
        expected = execute_trusted(conn, challenge.reference_sql)
        conn.execute("ROLLBACK TO reference")
        conn.execute("RELEASE reference")

        try:
            actual = execute_learner_sql(conn, sql, challenge.access_policy, timeout_seconds=timeout_seconds)
        except QueryError as error:
            _rollback(conn)
            return SubmissionOutcome(False, error.kind, error.message, None, False)

        verdict: Verdict = compare_results(expected, actual, ordered=challenge.ordered)
        if not verdict.passed:
            _rollback(conn)
            return SubmissionOutcome(False, verdict.code, verdict.message, actual, False)

        newly_completed = mark_completed(conn, challenge.id)
        conn.execute("COMMIT")
        return SubmissionOutcome(True, verdict.code, verdict.message, actual, newly_completed)
    except BaseException:
        _rollback(conn)
        raise
