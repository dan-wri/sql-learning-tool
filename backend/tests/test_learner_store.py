import sqlite3

import pytest

from app.learners.store import InvalidLearnerId, parse_learner_id
from tests.helpers import internal_state, visible_state


@pytest.mark.parametrize(
    "bad",
    ["", "not-a-uuid", "../../etc/passwd", "../template", "1234", "{12345678-1234-5678-1234-567812345678}",
     "12345678123456781234567812345678"],
)
def test_parse_learner_id_rejects_non_canonical(bad):
    with pytest.raises(InvalidLearnerId):
        parse_learner_id(bad)


def test_parse_learner_id_normalises_case(learner_id):
    assert parse_learner_id(learner_id.upper()) == learner_id


def test_ensure_creates_copy_of_template_once(store, learner_id):
    assert store.ensure(learner_id) is True
    assert store.ensure(learner_id) is False
    assert store.path_for(learner_id).exists()

    template = sqlite3.connect(store.template_path)
    try:
        with store.connection(learner_id) as conn:
            assert visible_state(conn) == visible_state(template)
    finally:
        template.close()


def test_learners_are_isolated(store, learner_id):
    other_id = "00000000-0000-4000-8000-000000000001"
    with store.connection(learner_id) as conn:
        conn.execute("DELETE FROM payments")

    with store.connection(other_id) as conn:
        assert conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0] > 0


def test_reset_restores_visible_and_progress_state(store, learner_id):
    with store.connection(learner_id) as conn:
        original_visible, original_internal = visible_state(conn), internal_state(conn)
        conn.execute(
            "INSERT INTO customers (first_name, last_name, email, city, country, signup_date) "
            "VALUES ('Ada', 'Lovelace', 'ada@example.com', 'London', 'UK', '2025-07-01')"
        )
        conn.execute("UPDATE products SET price = price * 2")
        conn.execute("INSERT INTO _app_progress VALUES ('select-01', '2025-07-01T00:00:00Z')")
        conn.execute("INSERT INTO _app_hints VALUES ('select-02', 2)")
        assert visible_state(conn) != original_visible

    store.reset(learner_id)

    with store.connection(learner_id) as conn:
        assert visible_state(conn) == original_visible
        assert internal_state(conn) == original_internal


def test_reset_discards_leftover_journal(store, learner_id):
    store.ensure(learner_id)
    path = store.path_for(learner_id)
    journal = path.with_name(path.name + "-journal")
    journal.write_bytes(b"stale")

    store.reset(learner_id)

    assert not journal.exists()
    with store.connection(learner_id) as conn:
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_connection_enables_foreign_keys(store, learner_id):
    with store.connection(learner_id) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO orders (customer_id, order_date, status) VALUES (9999, '2025-01-01', 'pending')")
