"""One submission = one transaction on the learner's database.

Reference and learner SQL both start from the same state: the reference runs inside a
savepoint that is rolled back before the learner's SQL runs. The transaction commits only
on a pass, so a failed submission never changes data or progress. Completed mutation
challenges run in review mode: they are validated in a throwaway sandbox rebuilt to the
pre-challenge state, and the learner's database is never written.
"""

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from app.challenges.registry import Challenge
from app.progress.service import completed_ids, mark_completed
from app.sql.executor import (
    TIMEOUT_SECONDS,
    QueryError,
    QueryResult,
    execute_learner_sql,
    execute_trusted,
    first_keyword,
)
from app.sql.snapshot import TableChanges, diff_snapshots, take_snapshot
from app.validation.result_validator import compare_results
from app.validation.state_validator import compare_changes


@dataclass(frozen=True)
class SubmissionOutcome:
    passed: bool
    code: str
    message: str
    result: QueryResult | None
    changes: dict[str, TableChanges] | None
    newly_completed: bool
    persisted: bool
    review_mode: bool


@dataclass(frozen=True)
class _Attempt:
    passed: bool
    code: str
    message: str
    result: QueryResult | None = None
    changes: dict[str, TableChanges] | None = None


def _rollback(conn: sqlite3.Connection) -> None:
    # SQLite can already have rolled back by itself (e.g. after an interrupt).
    if conn.in_transaction:
        conn.execute("ROLLBACK")


def _required_statement(operations: list[str]) -> str:
    article = "an" if operations[0][0] in "AEIOU" else "a"
    return f"{article} {' or '.join(operations)} statement"


def _attempt_query(conn: sqlite3.Connection, challenge: Challenge, sql: str, timeout_seconds: float) -> _Attempt:
    conn.execute("SAVEPOINT reference")
    expected = execute_trusted(conn, challenge.reference_sql)
    conn.execute("ROLLBACK TO reference")
    conn.execute("RELEASE reference")

    try:
        actual = execute_learner_sql(conn, sql, challenge.access_policy, timeout_seconds=timeout_seconds)
    except QueryError as error:
        return _Attempt(False, error.kind, error.message)
    verdict = compare_results(expected, actual, ordered=challenge.ordered)
    return _Attempt(verdict.passed, verdict.code, verdict.message, result=actual)


def _attempt_mutation(conn: sqlite3.Connection, challenge: Challenge, sql: str, timeout_seconds: float) -> _Attempt:
    if first_keyword(sql) in ("SELECT", "VALUES"):
        return _Attempt(False, "wrong_statement",
                        f"This challenge requires {_required_statement(challenge.write_operations)}. "
                        "A SELECT only reads data, so it can't complete this task.")

    before = take_snapshot(conn)
    conn.execute("SAVEPOINT reference")
    execute_trusted(conn, challenge.reference_sql)
    expected = diff_snapshots(before, take_snapshot(conn))
    conn.execute("ROLLBACK TO reference")
    conn.execute("RELEASE reference")

    try:
        result = execute_learner_sql(conn, sql, challenge.access_policy, timeout_seconds=timeout_seconds)
    except QueryError as error:
        return _Attempt(False, error.kind, error.message)
    actual = diff_snapshots(before, take_snapshot(conn))
    verdict = compare_changes(expected, actual, ignore_columns=challenge.ignore_columns)
    return _Attempt(verdict.passed, verdict.code, verdict.message,
                    result=result if result.columns else None, changes=actual)


def submit(conn: sqlite3.Connection, challenge: Challenge, sql: str, *,
           review_sandbox: Callable[[], sqlite3.Connection] | None = None,
           timeout_seconds: float = TIMEOUT_SECONDS) -> SubmissionOutcome:
    if challenge.kind == "mutation" and challenge.id in completed_ids(conn):
        return _submit_review(challenge, sql, review_sandbox, timeout_seconds)

    conn.execute("BEGIN IMMEDIATE")
    try:
        attempt_fn = _attempt_query if challenge.kind == "query" else _attempt_mutation
        attempt = attempt_fn(conn, challenge, sql, timeout_seconds)

        newly_completed = False
        if attempt.passed:
            newly_completed = mark_completed(conn, challenge.id)
            conn.execute("COMMIT")
        else:
            _rollback(conn)
        return SubmissionOutcome(
            passed=attempt.passed,
            code=attempt.code,
            message=attempt.message,
            result=attempt.result,
            changes=attempt.changes,
            newly_completed=newly_completed,
            persisted=attempt.passed,
            review_mode=False,
        )
    except BaseException:
        _rollback(conn)
        raise


def _submit_review(challenge: Challenge, sql: str, review_sandbox: Callable[[], sqlite3.Connection] | None,
                   timeout_seconds: float) -> SubmissionOutcome:
    if review_sandbox is None:
        raise RuntimeError("Review mode needs a sandbox factory")
    sandbox = review_sandbox()
    try:
        sandbox.execute("BEGIN IMMEDIATE")
        attempt = _attempt_mutation(sandbox, challenge, sql, timeout_seconds)
    finally:
        sandbox.close()
    return SubmissionOutcome(
        passed=attempt.passed,
        code=attempt.code,
        message=attempt.message,
        result=attempt.result,
        changes=attempt.changes,
        newly_completed=False,
        persisted=False,
        review_mode=True,
    )
