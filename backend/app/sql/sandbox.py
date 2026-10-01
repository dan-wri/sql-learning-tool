"""Throwaway databases for review mode, rebuilt to the state a learner had just before a challenge.

Every passed mutation must produce exactly the reference change, so "template + reference
solutions of all earlier challenges" is the canonical pre-challenge state.
"""

import sqlite3
from collections.abc import Callable
from pathlib import Path

from app.challenges.registry import Challenge
from app.sql.executor import execute_trusted


def canonical_state_before(template_path: Path, challenges: list[Challenge], challenge_id: str) -> sqlite3.Connection:
    sandbox = sqlite3.connect(":memory:", isolation_level=None)
    source = sqlite3.connect(f"file:{template_path}?mode=ro", uri=True)
    try:
        source.backup(sandbox)
    finally:
        source.close()
    sandbox.execute("PRAGMA foreign_keys = ON")
    for challenge in challenges:
        if challenge.id == challenge_id:
            return sandbox
        if challenge.kind == "mutation":
            execute_trusted(sandbox, challenge.reference_sql)
    sandbox.close()
    raise ValueError(f"Unknown challenge {challenge_id}")


def review_sandbox_factory(template_path: Path, challenges: list[Challenge],
                           challenge_id: str) -> Callable[[], sqlite3.Connection]:
    return lambda: canonical_state_before(template_path, challenges, challenge_id)
