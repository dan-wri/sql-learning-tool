"""Per-learner training databases: creation, locking, connections and reset."""

import os
import shutil
import sqlite3
import threading
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class InvalidLearnerId(ValueError):
    pass


def parse_learner_id(raw: str) -> str:
    """Accept only canonical UUID strings, because the id becomes part of a file path."""
    try:
        parsed = uuid.UUID(raw)
    except (ValueError, AttributeError, TypeError):
        raise InvalidLearnerId("Learner id must be a UUID") from None
    canonical = str(parsed)
    if raw.lower() != canonical:
        raise InvalidLearnerId("Learner id must be a UUID")
    return canonical


class LearnerStore:
    def __init__(self, template_path: Path, learners_dir: Path):
        self.template_path = template_path
        self.learners_dir = learners_dir
        self._locks: dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()

    def path_for(self, learner_id: str) -> Path:
        return self.learners_dir / f"{parse_learner_id(learner_id)}.db"

    def _lock_for(self, learner_id: str) -> threading.Lock:
        with self._locks_guard:
            return self._locks.setdefault(learner_id, threading.Lock())

    @contextmanager
    def locked(self, learner_id: str) -> Iterator[None]:
        """Serialise all work on one learner's database (submissions, reads, reset)."""
        learner_id = parse_learner_id(learner_id)
        with self._lock_for(learner_id):
            yield

    def ensure(self, learner_id: str) -> bool:
        """Create the learner's database from the template if needed. Returns True if created."""
        with self.locked(learner_id):
            return self._ensure_unlocked(learner_id)

    def reset(self, learner_id: str) -> None:
        """Replace the learner's database (data and progress) with a fresh copy of the template."""
        with self.locked(learner_id):
            self._copy_template_to(self.path_for(learner_id))

    @contextmanager
    def connection(self, learner_id: str) -> Iterator[sqlite3.Connection]:
        """Locked connection to the learner's database; transactions are controlled explicitly by callers."""
        with self.locked(learner_id):
            self._ensure_unlocked(learner_id)
            conn = sqlite3.connect(self.path_for(learner_id), isolation_level=None)
            try:
                conn.execute("PRAGMA foreign_keys = ON")
                yield conn
            finally:
                conn.close()

    def _ensure_unlocked(self, learner_id: str) -> bool:
        path = self.path_for(learner_id)
        if path.exists():
            return False
        self._copy_template_to(path)
        return True

    def _copy_template_to(self, path: Path) -> None:
        self.learners_dir.mkdir(parents=True, exist_ok=True)
        # A leftover journal from a crash would otherwise be "rolled back" into the fresh copy.
        for suffix in ("-journal", "-wal", "-shm"):
            path.with_name(path.name + suffix).unlink(missing_ok=True)
        tmp = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            shutil.copyfile(self.template_path, tmp)
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)
