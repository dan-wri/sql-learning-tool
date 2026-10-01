"""Capture learner-visible table contents and diff them, so mutations are judged by their effect on the data."""

import sqlite3
from dataclasses import dataclass

from app.sql.authorizer import is_hidden_table


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def visible_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name").fetchall()
    return [row[0] for row in rows if not is_hidden_table(row[0])]


@dataclass(frozen=True)
class TableState:
    columns: list[str]
    rows: dict[tuple, tuple]


Snapshot = dict[str, TableState]


@dataclass(frozen=True)
class TableChanges:
    table: str
    columns: list[str]
    inserted: list[tuple]
    updated: list[tuple[tuple, tuple]]
    deleted: list[tuple]


def take_snapshot(conn: sqlite3.Connection) -> Snapshot:
    """Must be called without a learner authorizer installed."""
    snapshot: Snapshot = {}
    for table in visible_tables(conn):
        quoted = quote_identifier(table)
        info = conn.execute(f"PRAGMA table_info({quoted})").fetchall()
        columns = [col[1] for col in info]
        key_positions = [columns.index(col[1]) for col in sorted((c for c in info if c[5]), key=lambda c: c[5])]
        if key_positions:
            rows = {tuple(row[i] for i in key_positions): tuple(row) for row in conn.execute(f"SELECT * FROM {quoted}")}
        else:
            rows = {(row[0],): tuple(row[1:]) for row in conn.execute(f"SELECT rowid, * FROM {quoted}")}
        snapshot[table] = TableState(columns, rows)
    return snapshot


def diff_snapshots(before: Snapshot, after: Snapshot) -> dict[str, TableChanges]:
    """Only tables that changed are included; rows are ordered by key for stable output."""
    changes: dict[str, TableChanges] = {}
    for table, new in after.items():
        old_rows = before[table].rows if table in before else {}
        new_rows = new.rows
        inserted = [new_rows[k] for k in sorted(new_rows.keys() - old_rows.keys(), key=repr)]
        deleted = [old_rows[k] for k in sorted(old_rows.keys() - new_rows.keys(), key=repr)]
        updated = [
            (old_rows[k], new_rows[k])
            for k in sorted(old_rows.keys() & new_rows.keys(), key=repr)
            if old_rows[k] != new_rows[k]
        ]
        if inserted or updated or deleted:
            changes[table] = TableChanges(table, new.columns, inserted, updated, deleted)
    return changes
