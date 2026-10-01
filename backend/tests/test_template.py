import sqlite3

from app.db.build_template import SEED_VERSION, build_template, ensure_template, read_seed_version
from tests.helpers import internal_state, visible_state

EXPECTED_TABLES = ["categories", "customers",
                   "order_items", "orders", "payments", "products"]


def _open(path):
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def test_template_has_training_and_app_tables(template):
    conn = _open(template.template_path)
    try:
        assert sorted(visible_state(conn)) == EXPECTED_TABLES
        assert sorted(internal_state(conn)) == [
            "_app_hints", "_app_meta", "_app_progress"]
        assert read_seed_version(conn) == SEED_VERSION
        assert conn.execute(
            "SELECT COUNT(*) FROM _app_progress").fetchone()[0] == 0
    finally:
        conn.close()


def test_template_data_is_populated_and_consistent(template):
    conn = _open(template.template_path)
    try:
        for table in EXPECTED_TABLES:
            assert conn.execute(
                f"SELECT COUNT(*) FROM {table}").fetchone()[0] > 0, table
        conn.execute("PRAGMA foreign_keys = ON")
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        # Some customers deliberately have no orders and some phones are NULL.
        assert conn.execute(
            "SELECT COUNT(*) FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders)"
        ).fetchone()[0] > 0
        assert conn.execute(
            "SELECT COUNT(*) FROM customers WHERE phone IS NULL").fetchone()[0] > 0
    finally:
        conn.close()


def test_template_build_is_deterministic(tmp_path):
    a, b = tmp_path / "a.db", tmp_path / "b.db"
    build_template(a)
    build_template(b)
    conn_a, conn_b = _open(a), _open(b)
    try:
        assert visible_state(conn_a) == visible_state(conn_b)
    finally:
        conn_a.close()
        conn_b.close()


def test_ensure_template_rebuilds_outdated_version(settings):
    build_template(settings.template_path)
    conn = sqlite3.connect(settings.template_path)
    conn.execute("UPDATE _app_meta SET value = '0' WHERE key = 'seed_version'")
    conn.commit()
    conn.close()

    ensure_template(settings.template_path)

    conn = _open(settings.template_path)
    try:
        assert read_seed_version(conn) == SEED_VERSION
    finally:
        conn.close()
