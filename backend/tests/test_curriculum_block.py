"""Behaviour of the approved Levels 1-10: validation, progression through the API, story metadata and secrecy."""

import json

import pytest

from app.challenges.registry import load_challenges
from app.config import CHALLENGES_DIR
from app.sql.orchestrator import submit
from tests.helpers import visible_state

CHALLENGES = load_challenges(CHALLENGES_DIR).all()
BY_LEVEL = {c.level: c for c in CHALLENGES}

# (level, learner SQL, expected failure code)
WRONG_ANSWERS = [
    (1, "SELECT name FROM categories", "column_count"),
    (1, "SELECT * FROM categories WHERE category_id <= 3", "row_count"),
    (2, "SELECT first_name, last_name FROM customers", "column_count"),
    (2, "SELECT email, last_name, first_name FROM customers", "column_order"),
    (3, "SELECT first_name, last_name, email, city FROM customers", "row_count"),
    (3, "SELECT first_name, last_name, email, city FROM customers WHERE country = 'Ireland'", "row_count"),
    (3, "SELECT first_name, last_name, email, city FROM customers WHERE country = 'uk '", "row_count"),
    (4, "SELECT name, price FROM products WHERE price < 10", "row_count"),
    (4, "SELECT name, price FROM products WHERE price > 20", "row_count"),
    (5, "SELECT name, price, stock_quantity FROM products WHERE is_active = 1", "row_count"),
    (5, "SELECT name, price, stock_quantity FROM products WHERE is_active = 1 OR stock_quantity > 0", "row_count"),
    (6, "SELECT name, stock_quantity, is_active FROM products WHERE stock_quantity = 0 AND is_active = 0", "row_count"),
    (6, "SELECT name, stock_quantity, is_active FROM products WHERE stock_quantity = 0", "row_count"),
    (7, "SELECT name, price FROM products ORDER BY price DESC", "row_order"),
    (7, "SELECT name, price FROM products ORDER BY price DESC, name DESC", "row_order"),
    (7, "SELECT name, price FROM products ORDER BY price ASC, name ASC", "row_order"),
    (7, "SELECT name, price FROM products ORDER BY name", "row_order"),
    (8, "SELECT name, price FROM products WHERE price > 50 ORDER BY price DESC", "row_order"),
    (8, "SELECT name, price FROM products WHERE price > 50 ORDER BY price", "row_order"),
    (8, "SELECT name, price FROM products ORDER BY price DESC, name", "row_count"),
    (9, "SELECT name, stock_quantity FROM products WHERE is_active = 1 ORDER BY stock_quantity DESC, name", "row_count"),
    (9, "SELECT name, stock_quantity FROM products WHERE is_active = 1 ORDER BY stock_quantity DESC, name LIMIT 6",
     "row_count"),
    (9, "SELECT name, stock_quantity FROM products WHERE is_active = 1 ORDER BY stock_quantity, name LIMIT 5",
     "wrong_values"),
    (9, "SELECT name, stock_quantity FROM products WHERE is_active = 1 ORDER BY stock_quantity DESC, name DESC LIMIT 5",
     "wrong_values"),
    (9, "SELECT name, stock_quantity FROM products WHERE is_active = 1 ORDER BY name LIMIT 5", "wrong_values"),
    (10, "SELECT customer_id, first_name, last_name, email FROM customers WHERE phone IS NOT NULL", "row_count"),
    (10, "SELECT customer_id, first_name, last_name, email FROM customers WHERE phone = ''", "row_count"),
    (10, "SELECT customer_id, first_name, last_name, email FROM customers WHERE phone = NULL", "row_count"),
    (10, "SELECT customer_id, first_name, last_name, email FROM customers", "row_count"),
]


@pytest.fixture
def conn(store, learner_id):
    with store.connection(learner_id) as connection:
        yield connection


@pytest.mark.parametrize("level, sql, code", WRONG_ANSWERS)
def test_incorrect_answers_fail_without_changing_anything(conn, level, sql, code):
    before = visible_state(conn)
    outcome = submit(conn, BY_LEVEL[level], sql)
    assert not outcome.passed, outcome.message
    assert outcome.code == code
    assert not outcome.persisted
    assert visible_state(conn) == before


def test_unordered_levels_accept_any_row_order(conn):
    for level, sql in [
        (3, "SELECT first_name, last_name, email, city FROM customers WHERE country = 'UK' ORDER BY last_name DESC"),
        (4, "SELECT name, price FROM products WHERE price < 20 ORDER BY price DESC"),
        (10, "SELECT customer_id, first_name, last_name, email FROM customers WHERE phone IS NULL "
             "ORDER BY customer_id DESC"),
    ]:
        assert submit(conn, BY_LEVEL[level], sql).passed, level


def test_ordered_levels_require_the_exact_order(conn):
    reversed_sql = "SELECT name, price FROM products WHERE price > 50 ORDER BY price ASC, name DESC"
    assert submit(conn, BY_LEVEL[8], reversed_sql).code == "row_order"
    for level in (7, 8, 9):
        assert submit(conn, BY_LEVEL[level], BY_LEVEL[level].reference_sql).passed


def test_level_nine_returns_exactly_the_right_five(conn):
    outcome = submit(conn, BY_LEVEL[9], BY_LEVEL[9].reference_sql)
    rows = outcome.result.rows
    assert len(rows) == 5
    stocks = [r[1] for r in rows]
    assert stocks == sorted(stocks, reverse=True)
    expected = conn.execute("SELECT name, stock_quantity FROM products WHERE is_active = 1 "
                            "ORDER BY stock_quantity DESC, name ASC LIMIT 5").fetchall()
    assert [tuple(r) for r in rows] == expected
    # The fifth and sixth active products tie on stock, so the name tie-breaker decides the cut.
    sixth = conn.execute("SELECT stock_quantity FROM products WHERE is_active = 1 "
                         "ORDER BY stock_quantity DESC, name LIMIT 1 OFFSET 5").fetchone()[0]
    assert sixth == stocks[-1]


def test_level_ten_only_returns_customers_with_null_phone(conn):
    rows = submit(conn, BY_LEVEL[10], BY_LEVEL[10].reference_sql).result.rows
    assert rows
    ids = [r[0] for r in rows]
    nulls = [r[0] for r in conn.execute("SELECT customer_id FROM customers WHERE phone IS NULL")]
    assert sorted(ids) == sorted(nulls)
    assert conn.execute("SELECT COUNT(*) FROM customers WHERE phone = ''").fetchone()[0] == 0


def test_level_seven_and_eight_orders_have_real_ties(conn):
    ties = conn.execute("SELECT price FROM products GROUP BY price HAVING COUNT(*) > 1").fetchall()
    assert any(price > 50 for (price,) in ties)
    assert any(price < 50 for (price,) in ties)


@pytest.fixture
def api(client, learner_id):
    headers = {"X-Learner-Id": learner_id}

    class Api:
        def get(self, path):
            return client.get(f"/api{path}", headers=headers)

        def post(self, path, body=None):
            return client.post(f"/api{path}", headers=headers, json=body)

        def submit(self, challenge, sql=None):
            return self.post(f"/challenges/{challenge.id}/submit", {"sql": sql or challenge.reference_sql})

        def statuses(self):
            return [c["status"] for c in self.get("/challenges").json()]

    return Api()


def test_challenge_list_exposes_ten_levels_with_metadata(api):
    listing = api.get("/challenges").json()
    assert [c["level"] for c in listing] == list(range(1, 11))
    assert [c["title"] for c in listing] == [c.title for c in CHALLENGES]
    assert {c["chapter"] for c in listing} == {1}
    assert {c["kind"] for c in listing} == {"query"}
    assert api.statuses() == ["unlocked"] + ["locked"] * 9


def test_challenge_detail_separates_story_from_task(api):
    for challenge in CHALLENGES:
        detail = api.get(f"/challenges/{challenge.id}").json()
        assert detail["level"] == challenge.level
        assert detail["title"] == challenge.title
        assert detail["chapter"] == 1
        assert detail["story"] == challenge.story
        assert detail["instructions"] == challenge.instructions
        assert detail["concepts"] == challenge.concepts
        assert detail["story"] != detail["instructions"]
        assert detail["total_hints"] == 3
        assert detail["hints"] == []
        assert api.submit(challenge).json()["passed"]


def test_api_progression_one_level_at_a_time(api):
    for position, challenge in enumerate(CHALLENGES):
        assert api.statuses()[position] == "unlocked"
        if position + 1 < len(CHALLENGES):
            assert api.submit(CHALLENGES[position + 1]).status_code == 403
        body = api.submit(challenge).json()
        assert body["passed"] and body["newly_completed"]
        expected_next = CHALLENGES[position + 1].id if position + 1 < len(CHALLENGES) else None
        assert body["next_challenge_id"] == expected_next
    assert api.statuses() == ["completed"] * 10
    assert api.post("/learner/reset").status_code == 200
    assert api.statuses() == ["unlocked"] + ["locked"] * 9


def test_failed_submission_does_not_unlock_next_level(api):
    body = api.submit(CHALLENGES[0], "SELECT name FROM categories").json()
    assert not body["passed"]
    assert api.statuses() == ["unlocked"] + ["locked"] * 9


def test_completed_level_can_be_reopened_and_resubmitted(api):
    first = CHALLENGES[0]
    api.submit(first)
    detail = api.get(f"/challenges/{first.id}").json()
    assert detail["status"] == "completed" and detail["review_mode"] is True
    again = api.submit(first).json()
    assert again["passed"] and not again["newly_completed"] and again["review_mode"]
    assert api.statuses()[:2] == ["completed", "unlocked"]


def test_reference_sql_never_leaks_through_any_endpoint(api):
    texts = []
    references = [" ".join(c.reference_sql.split()).rstrip(";").lower() for c in CHALLENGES]
    texts.append(api.get("/challenges"))
    for challenge in CHALLENGES:
        texts.append(api.get(f"/challenges/{challenge.id}"))
        for _ in challenge.hints:
            texts.append(api.post(f"/challenges/{challenge.id}/hints"))
        texts.append(api.submit(challenge, "SELECT 1"))
        texts.append(api.submit(challenge, "not sql"))
        texts.append(api.submit(challenge))
        texts.append(api.get(f"/challenges/{challenge.id}"))
    for response in texts:
        body = " ".join(json.dumps(response.json()).split()).lower()
        assert "reference_sql" not in body
        for reference in references:
            assert reference not in body
