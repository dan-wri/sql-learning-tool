"""Progress and hint state, stored in the learner's own _app_* tables."""

import sqlite3
from datetime import UTC, datetime
from typing import Literal

from app.challenges.registry import ChallengeRegistry

Status = Literal["completed", "unlocked", "locked"]


def completed_ids(conn: sqlite3.Connection) -> set[str]:
    return {row[0] for row in conn.execute("SELECT challenge_id FROM _app_progress")}


def mark_completed(conn: sqlite3.Connection, challenge_id: str) -> bool:
    """Record completion; returns True only the first time."""
    cursor = conn.execute(
        "INSERT OR IGNORE INTO _app_progress (challenge_id, completed_at) VALUES (?, ?)",
        (challenge_id, datetime.now(UTC).isoformat(timespec="seconds")),
    )
    return cursor.rowcount == 1


def status_of(registry: ChallengeRegistry, completed: set[str], challenge_id: str) -> Status:
    if challenge_id in completed:
        return "completed"
    previous = registry.previous(challenge_id)
    if previous is None or previous.id in completed:
        return "unlocked"
    return "locked"


def hints_revealed(conn: sqlite3.Connection, challenge_id: str) -> int:
    row = conn.execute(
        "SELECT hints_revealed FROM _app_hints WHERE challenge_id = ?", (challenge_id,)).fetchone()
    return row[0] if row else 0


def reveal_next_hint(conn: sqlite3.Connection, challenge_id: str, total_hints: int) -> int:
    conn.execute(
        "INSERT INTO _app_hints (challenge_id, hints_revealed) VALUES (?, 1) "
        "ON CONFLICT (challenge_id) DO UPDATE SET hints_revealed = MIN(hints_revealed + 1, ?)",
        (challenge_id, total_hints),
    )
    return hints_revealed(conn, challenge_id)
