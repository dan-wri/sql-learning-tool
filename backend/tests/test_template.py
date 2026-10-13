import pytest
import sqlite3

from app.db.build_template import SEED_VERSION, build_template, ensure_template, read_seed_version
from tests.helpers import internal_state, visible_state

EXPECTED_TABLES = ["categories", "customers", "order_items", "orders", "payments", "product_reviews", "products",
                   "returns"]


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


@pytest.fixture
def db(template):
    conn = _open(template.template_path)
    yield lambda sql: conn.execute(sql).fetchall()
    conn.close()


def scalar(db, sql):
    return db(sql)[0][0]


def test_seed_version_is_bumped_for_the_expanded_schema():
    assert SEED_VERSION >= 2


def test_order_lifecycle_dates_follow_status(db):
    assert scalar(db, "SELECT COUNT(*) FROM orders WHERE status IN ('pending', 'cancelled') "
                      "AND (shipped_date IS NOT NULL OR delivered_date IS NOT NULL)") == 0
    assert scalar(db, "SELECT COUNT(*) FROM orders WHERE status = 'shipped' "
                      "AND (shipped_date IS NULL OR delivered_date IS NOT NULL)") == 0
    assert scalar(db, "SELECT COUNT(*) FROM orders WHERE status = 'delivered' "
                      "AND NOT (shipped_date IS NOT NULL AND delivered_date IS NOT NULL "
                      "AND order_date <= shipped_date AND shipped_date <= delivered_date)") == 0
    assert {r[0] for r in db("SELECT DISTINCT status FROM orders")} == {"pending", "shipped", "delivered", "cancelled"}


def test_volumes_and_monthly_coverage(db):
    assert 75 <= scalar(db, "SELECT COUNT(*) FROM customers") <= 90
    assert 350 <= scalar(db, "SELECT COUNT(*) FROM orders") <= 420
    assert db("SELECT substr(order_date, 1, 7) m, COUNT(*) n FROM orders WHERE order_date >= '2024' "
              "GROUP BY m HAVING n < 12") == []
    assert scalar(db, "SELECT COUNT(DISTINCT substr(order_date, 1, 7)) FROM orders WHERE order_date >= '2024'") == 24
    assert scalar(db, "SELECT MAX(order_date) FROM orders") < "2026-01-05"


def test_customer_fixtures(db):
    assert scalar(db, "SELECT COUNT(*) FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders)") >= 8
    assert scalar(db, "SELECT COUNT(*) FROM customers WHERE country = 'UK' AND phone IS NULL "
                      "AND email <> 'qa.test@brightcart.example'") >= 8
    assert db("SELECT customer_id FROM customers WHERE email = 'qa.test@brightcart.example'")
    qa = "(SELECT customer_id FROM customers WHERE email = 'qa.test@brightcart.example')"
    for table in ("orders", "product_reviews"):
        assert scalar(db, f"SELECT COUNT(*) FROM {table} WHERE customer_id = {qa}") == 0
    assert scalar(db, f"SELECT COUNT(*) FROM customers WHERE referred_by_customer_id = {qa}") == 0
    assert scalar(db, "SELECT COUNT(*) FROM customers WHERE country = 'Sweden'") == 0
    assert scalar(db, "SELECT COUNT(*) FROM customers WHERE first_name = 'Grace'") == 3
    assert scalar(db, "SELECT COUNT(*) FROM customers WHERE email = 'grace.hopper@example.com'") == 0
    assert len(db("SELECT 1 FROM customers GROUP BY first_name, last_name HAVING COUNT(*) > 1")) == 3
    assert scalar(db, "SELECT COUNT(*) FROM customers WHERE signup_date BETWEEN '2025-10-01' AND '2025-12-31'") > 0
    assert scalar(db, "SELECT COUNT(*) FROM customers WHERE last_name LIKE 'W%'") > 0


def test_dirty_emails_normalise_without_collisions(db):
    assert 4 <= scalar(db, "SELECT COUNT(*) FROM customers WHERE email <> lower(trim(email))") <= 6
    assert db("SELECT lower(trim(email)) FROM customers GROUP BY 1 HAVING COUNT(*) > 1") == []


def test_referrals_include_a_two_step_chain(db):
    assert 10 <= scalar(db, "SELECT COUNT(*) FROM customers WHERE referred_by_customer_id IS NOT NULL") <= 15
    assert scalar(db, "SELECT COUNT(*) FROM customers c JOIN customers r ON c.referred_by_customer_id = r.customer_id "
                      "WHERE r.referred_by_customer_id IS NOT NULL") >= 1


def test_finance_fixtures(db):
    totals = ("(SELECT order_id, ROUND(SUM(quantity * unit_price), 2) AS total FROM order_items GROUP BY order_id)")
    paid = "(SELECT order_id, ROUND(SUM(amount), 2) AS paid FROM payments GROUP BY order_id)"
    assert 2 <= scalar(db, "SELECT COUNT(*) FROM orders o WHERE status = 'delivered' AND NOT EXISTS "
                           "(SELECT 1 FROM payments p WHERE p.order_id = o.order_id)") <= 3
    assert 1 <= scalar(db, f"SELECT COUNT(*) FROM {totals} t JOIN {paid} p USING (order_id) WHERE p.paid < t.total") <= 2
    assert scalar(db, "SELECT COUNT(*) FROM (SELECT order_id FROM payments GROUP BY order_id HAVING COUNT(*) = 2)") >= 1
    assert scalar(db, f"SELECT COUNT(*) FROM {totals} t JOIN {paid} p USING (order_id) WHERE p.paid <> t.total") <= 3


def test_returns_and_refund_anomalies(db):
    assert 18 <= scalar(db, "SELECT COUNT(*) FROM returns") <= 30
    wrong = scalar(db, "SELECT COUNT(*) FROM returns r JOIN order_items i USING (order_item_id) "
                       "WHERE r.refund_amount <> ROUND(r.quantity * i.unit_price, 2)")
    assert 2 <= wrong <= 3
    assert scalar(db, "SELECT COUNT(*) FROM returns r JOIN order_items i USING (order_item_id) "
                      "JOIN products p USING (product_id) WHERE p.name = 'USB-C Charger'") >= 1


def test_reviews(db):
    assert 70 <= scalar(db, "SELECT COUNT(*) FROM product_reviews") <= 100
    assert 3 <= scalar(db, "SELECT COUNT(*) FROM product_reviews WHERE review_text LIKE 'BOT:%'") <= 4
    verified = ("EXISTS (SELECT 1 FROM orders o JOIN order_items i USING (order_id) "
                "WHERE o.customer_id = r.customer_id AND i.product_id = r.product_id)")
    assert scalar(db, f"SELECT COUNT(*) FROM product_reviews r WHERE {verified}") > 0
    assert scalar(db, f"SELECT COUNT(*) FROM product_reviews r WHERE NOT {verified}") > 0


def test_price_history_and_recall_data(db):
    assert scalar(db, "SELECT COUNT(DISTINCT product_id) FROM order_items i "
                      "JOIN products p USING (product_id) WHERE i.unit_price <> p.price") >= 3
    assert scalar(db, "SELECT COUNT(*) FROM order_items i JOIN products p USING (product_id) "
                      "WHERE p.name = 'USB-C Charger'") >= 20


def test_holiday_delivery_delays_and_country_coverage(db):
    assert scalar(db, "SELECT COUNT(*) FROM orders WHERE status = 'delivered' AND order_date >= '2025-11-15' "
                      "AND julianday(delivered_date) - julianday(order_date) > 12") >= 5
    assert scalar(db, "SELECT COUNT(*) FROM orders WHERE status = 'delivered' AND order_date < '2025-10-01' "
                      "AND julianday(delivered_date) - julianday(order_date) > 12") == 0
    eligible = db("SELECT c.country FROM orders o JOIN customers c USING (customer_id) "
                  "WHERE o.order_date LIKE '2025%' GROUP BY c.country HAVING COUNT(DISTINCT o.customer_id) >= 5")
    assert len(eligible) >= 5
    december = db("SELECT c.country FROM orders o JOIN customers c USING (customer_id) "
                  "WHERE o.status = 'delivered' AND o.order_date LIKE '2025-12%' "
                  "GROUP BY c.country HAVING COUNT(*) >= 5")
    assert len(december) >= 5


def test_catalogue_fixtures(db):
    assert [r[0] for r in db("SELECT category_id FROM categories ORDER BY category_id")] == [1, 2, 3, 4, 5, 6]
    assert scalar(db, "SELECT COUNT(*) FROM products WHERE stock_quantity = 0") > 0
    assert scalar(db, "SELECT COUNT(*) FROM products WHERE is_active = 0") > 0
    assert scalar(db, "SELECT COUNT(*) FROM products WHERE is_active = 1 AND stock_quantity > 0") >= 5
