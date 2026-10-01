import pytest

from app.sql.snapshot import TableChanges, diff_snapshots, take_snapshot, visible_tables
from app.validation.state_validator import compare_changes

CUSTOMER_COLUMNS = ["customer_id", "first_name", "last_name", "email", "phone", "city", "country", "signup_date"]
GRACE = (61, "Grace", "Hopper", "grace@example.com", None, "London", "UK", "2025-07-01")


def changes(inserted=(), updated=(), deleted=(), table="customers", columns=CUSTOMER_COLUMNS):
    return {table: TableChanges(table, columns, list(inserted), list(updated), list(deleted))}


@pytest.fixture
def conn(store, learner_id):
    with store.connection(learner_id) as connection:
        connection.execute("BEGIN")
        yield connection
        connection.execute("ROLLBACK")


def test_visible_tables_exclude_internal_tables(conn):
    assert visible_tables(conn) == ["categories", "customers", "order_items", "orders", "payments", "products"]


def test_diff_detects_inserts_updates_and_deletes(conn):
    before = take_snapshot(conn)
    conn.execute("INSERT INTO categories (name) VALUES ('Garden')")
    conn.execute("UPDATE products SET price = 1 WHERE product_id = 2")
    conn.execute("DELETE FROM payments WHERE payment_id = 1")
    diff = diff_snapshots(before, take_snapshot(conn))

    assert sorted(diff) == ["categories", "payments", "products"]
    assert diff["categories"].inserted == [(7, "Garden")]
    (old, new), = diff["products"].updated
    assert (old[0], old[3], new[3]) == (2, 39.99, 1)
    assert [row[0] for row in diff["payments"].deleted] == [1]


def test_no_op_update_is_not_a_change(conn):
    before = take_snapshot(conn)
    conn.execute("UPDATE products SET price = price")
    assert diff_snapshots(before, take_snapshot(conn)) == {}


def test_identical_changes_pass():
    assert compare_changes(changes([GRACE]), changes([GRACE]), ignore_columns={}).passed


def test_int_and_float_values_are_equivalent():
    floaty = changes([GRACE], table="t", columns=CUSTOMER_COLUMNS)
    assert compare_changes(floaty, changes([(61.0, *GRACE[1:])], table="t"), ignore_columns={}).passed


def test_nothing_inserted():
    verdict = compare_changes(changes([GRACE]), {}, ignore_columns={})
    assert verdict.code == "row_count"
    assert verdict.message.startswith("Your INSERT created 0 rows")
    assert "expects 1" in verdict.message


def test_too_many_inserted():
    second = (62, *GRACE[1:3], "other@example.com", *GRACE[4:])
    verdict = compare_changes(changes([GRACE]), changes([GRACE, second]), ignore_columns={})
    assert verdict.code == "row_count"
    assert "created 2 rows" in verdict.message


def test_wrong_values_name_the_columns_without_leaking_expected_values():
    wrong = (61, "Grace", "Hopper", "grace@example.org", None, "Londn", "UK", "2025-07-01")
    verdict = compare_changes(changes([GRACE]), changes([wrong]), ignore_columns={})
    assert verdict.code == "wrong_values"
    assert "email" in verdict.message and "city" in verdict.message
    assert "first_name" not in verdict.message
    assert "grace@example.com" not in verdict.message and "London" not in verdict.message


def test_side_effect_on_another_table_fails():
    actual = {**changes([GRACE]), **changes(deleted=[(1, "Electronics")], table="categories",
                                            columns=["category_id", "name"])}
    verdict = compare_changes(changes([GRACE]), actual, ignore_columns={})
    assert verdict.code == "side_effect"
    assert "categories" in verdict.message


def test_unexpected_update_fails():
    old = (1, "Ava", "Evans", "a@example.com", None, "Dublin", "Ireland", "2024-07-26")
    actual = {"customers": TableChanges("customers", CUSTOMER_COLUMNS, [GRACE], [(old, (*old[:5], "Paris", *old[6:]))], [])}
    verdict = compare_changes(changes([GRACE]), actual, ignore_columns={})
    assert verdict.code == "row_count"
    assert "updated 1 row" in verdict.message


def test_ignored_columns_are_not_compared():
    other_date = (*GRACE[:7], "2030-01-01")
    assert not compare_changes(changes([GRACE]), changes([other_date]), ignore_columns={}).passed
    assert compare_changes(changes([GRACE]), changes([other_date]),
                           ignore_columns={"customers": ["signup_date"]}).passed


def test_updates_compare_rows_by_key():
    before = (5, "Old")
    expected = changes(updated=[(before, (5, "New"))], table="t", columns=["id", "name"])
    wrong_row = changes(updated=[((6, "Old"), (6, "New"))], table="t", columns=["id", "name"])
    wrong_value = changes(updated=[(before, (5, "Neu"))], table="t", columns=["id", "name"])
    assert compare_changes(expected, wrong_row, ignore_columns={}).code == "wrong_rows"
    assert compare_changes(expected, wrong_value, ignore_columns={}).code == "wrong_values"


def test_deletes_compare_rows():
    expected = changes(deleted=[(5, "a")], table="t", columns=["id", "name"])
    actual = changes(deleted=[(6, "b")], table="t", columns=["id", "name"])
    assert compare_changes(expected, actual, ignore_columns={}).code == "wrong_rows"
