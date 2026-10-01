"""Compare database contents by meaning, not by SQLite's file representation."""

import sqlite3


def _tables(conn: sqlite3.Connection, internal: bool) -> list[str]:
    rows = conn.execute("SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name").fetchall()
    names = [r[0] for r in rows if not r[0].startswith("sqlite_")]
    return [n for n in names if n.startswith("_app_") == internal]


def _dump(conn: sqlite3.Connection, tables: list[str]) -> dict[str, list[tuple]]:
    return {t: sorted(conn.execute(f'SELECT * FROM "{t}"').fetchall(), key=repr) for t in tables}


def visible_state(conn: sqlite3.Connection) -> dict[str, list[tuple]]:
    return _dump(conn, _tables(conn, internal=False))


def internal_state(conn: sqlite3.Connection) -> dict[str, list[tuple]]:
    return _dump(conn, _tables(conn, internal=True))
