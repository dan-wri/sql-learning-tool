"""Build the pristine template database that every learner database is copied from.

Run directly to (re)build: python -m app.db.build_template
"""

import os
import sqlite3
from pathlib import Path

from app.config import Settings
from app.db.seed_data import generate

# Bump whenever schema.sql, app_tables.sql or seed_data.py changes, so existing learner DBs show as stale.
SEED_VERSION = 1

DB_DIR = Path(__file__).resolve().parent
SCHEMA_SQL = DB_DIR / "schema.sql"
APP_TABLES_SQL = DB_DIR / "app_tables.sql"


def build_template(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    tmp.unlink(missing_ok=True)

    conn = sqlite3.connect(tmp)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_SQL.read_text())
        conn.executescript(APP_TABLES_SQL.read_text())
        for table, rows in generate().items():
            placeholders = ", ".join("?" * len(rows[0]))
            conn.executemany(
                f"INSERT INTO {table} VALUES ({placeholders})", rows)
        conn.execute(
            "INSERT INTO _app_meta (key, value) VALUES ('seed_version', ?)", (str(SEED_VERSION),))
        conn.commit()
    finally:
        conn.close()

    os.replace(tmp, dest)


def read_seed_version(conn: sqlite3.Connection) -> int | None:
    row = conn.execute(
        "SELECT value FROM _app_meta WHERE key = 'seed_version'").fetchone()
    return int(row[0]) if row else None


def ensure_template(dest: Path) -> None:
    """Build the template if it is missing or was built from an older seed version."""
    if dest.exists():
        conn = sqlite3.connect(f"file:{dest}?mode=ro", uri=True)
        try:
            if read_seed_version(conn) == SEED_VERSION:
                return
        except sqlite3.DatabaseError:
            pass
        finally:
            conn.close()
    build_template(dest)


if __name__ == "__main__":
    path = Settings.from_env().template_path
    build_template(path)
    print(f"Built template database (seed version {SEED_VERSION}) at {path}")
