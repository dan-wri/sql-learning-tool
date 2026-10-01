"""Compare database contents by meaning, not by SQLite's file representation."""

import sqlite3


def _tables(conn: sqlite3.Connection, internal: bool) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name").fetchall()
    names = [r[0] for r in rows if not r[0].startswith("sqlite_")]
    return [n for n in names if n.startswith("_app_") == internal]


def _dump(conn: sqlite3.Connection, tables: list[str]) -> dict[str, list[tuple]]:
    return {t: sorted(conn.execute(f'SELECT * FROM "{t}"').fetchall(), key=repr) for t in tables}


def visible_state(conn: sqlite3.Connection) -> dict[str, list[tuple]]:
    return _dump(conn, _tables(conn, internal=False))


def internal_state(conn: sqlite3.Connection) -> dict[str, list[tuple]]:
    return _dump(conn, _tables(conn, internal=True))


def replay_until(conn: sqlite3.Connection, challenges: list, stop_id: str) -> None:
    """Pass every challenge before stop_id with its reference solution, as a learner would."""
    from app.sql.orchestrator import submit

    for challenge in challenges:
        if challenge.id == stop_id:
            return
        outcome = submit(conn, challenge, challenge.reference_sql)
        assert outcome.passed, f"{challenge.id}: {outcome.message}"
    raise AssertionError(f"Unknown challenge {stop_id}")
