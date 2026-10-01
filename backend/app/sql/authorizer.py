"""SQLite authorizer enforcing what learner SQL may touch."""

import sqlite3
from dataclasses import dataclass, field

WRITE_ACTIONS = {
    sqlite3.SQLITE_INSERT: "INSERT",
    sqlite3.SQLITE_UPDATE: "UPDATE",
    sqlite3.SQLITE_DELETE: "DELETE",
}

STRUCTURE_ACTIONS = {
    getattr(sqlite3, name)
    for name in dir(sqlite3)
    if name.startswith(("SQLITE_CREATE_", "SQLITE_DROP_")) or name in ("SQLITE_ALTER_TABLE", "SQLITE_REINDEX",
                                                                       "SQLITE_ANALYZE")
}

DENIED_FUNCTIONS = {"load_extension"}

MSG_READ_ONLY = "This challenge is about reading data, so only SELECT queries are allowed."
MSG_STRUCTURE = "Changing the database structure (CREATE, DROP, ALTER, indexes, triggers) isn't allowed."
MSG_TRANSACTION = "Transactions are managed for you, so BEGIN, COMMIT, ROLLBACK and SAVEPOINT can't be used."
MSG_PRAGMA = "PRAGMA statements aren't allowed."
MSG_ATTACH = "Attaching other databases isn't allowed."
MSG_HIDDEN_TABLE = "That table isn't available. Use the tables listed in the schema panel."
MSG_DEFAULT = "This kind of statement isn't allowed."


def is_hidden_table(name: str | None) -> bool:
    lowered = (name or "").lower()
    return lowered.startswith(("_app_", "sqlite_", "pragma_"))


@dataclass(frozen=True)
class AccessPolicy:
    """What a challenge permits beyond reading visible tables. Empty means read-only."""

    write_operations: frozenset[str] = field(default_factory=frozenset)
    writable_tables: frozenset[str] = field(default_factory=frozenset)

    @property
    def read_only(self) -> bool:
        return not self.write_operations


READ_ONLY = AccessPolicy()


class Authorizer:
    """Callable for Connection.set_authorizer that records why it denied something."""

    def __init__(self, policy: AccessPolicy):
        self.policy = policy
        self.denial: str | None = None

    def _deny(self, message: str) -> int:
        if self.denial is None:
            self.denial = message
        return sqlite3.SQLITE_DENY

    def __call__(self, action: int, arg1: str | None, arg2: str | None, _db: str | None, _source: str | None) -> int:
        if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ:
            return self._deny(MSG_HIDDEN_TABLE) if is_hidden_table(arg1) else sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION:
            return self._deny(MSG_DEFAULT) if (arg2 or "").lower() in DENIED_FUNCTIONS else sqlite3.SQLITE_OK
        if action in WRITE_ACTIONS:
            return self._authorize_write(WRITE_ACTIONS[action], arg1)
        if action in (sqlite3.SQLITE_TRANSACTION, sqlite3.SQLITE_SAVEPOINT):
            return self._deny(MSG_TRANSACTION)
        if action == sqlite3.SQLITE_PRAGMA:
            return self._deny(MSG_PRAGMA)
        if action in (sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH):
            return self._deny(MSG_ATTACH)
        if action in STRUCTURE_ACTIONS:
            return self._deny(MSG_STRUCTURE)
        return self._deny(MSG_DEFAULT)

    def _authorize_write(self, operation: str, table: str | None) -> int:
        if self.policy.read_only:
            return self._deny(MSG_READ_ONLY)
        if is_hidden_table(table):
            return self._deny(MSG_HIDDEN_TABLE)
        if operation not in self.policy.write_operations:
            allowed = ", ".join(sorted(self.policy.write_operations))
            return self._deny(f"This challenge only allows {allowed}; {operation} isn't allowed here.")
        if table not in self.policy.writable_tables:
            allowed = ", ".join(
                sorted(t for t in self.policy.writable_tables if not is_hidden_table(t)))
            return self._deny(f"This challenge only allows changes to {allowed}; {table} can't be modified here.")
        return sqlite3.SQLITE_OK
