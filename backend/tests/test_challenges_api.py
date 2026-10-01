import json

import pytest

from app.challenges.registry import load_challenges
from app.config import CHALLENGES_DIR

CHALLENGES = load_challenges(CHALLENGES_DIR).all()
FIRST, SECOND = CHALLENGES[0], CHALLENGES[1]


@pytest.fixture
def api(client, learner_id):
    headers = {"X-Learner-Id": learner_id}

    class Api:
        def get(self, path):
            return client.get(f"/api{path}", headers=headers)

        def post(self, path, body=None):
            return client.post(f"/api{path}", headers=headers, json=body)

        def submit(self, challenge_id, sql):
            return self.post(f"/challenges/{challenge_id}/submit", {"sql": sql})

        def statuses(self):
            return {c["id"]: c["status"] for c in self.get("/challenges").json()}

    return Api()


def test_initial_progression(api):
    statuses = api.statuses()
    assert statuses[FIRST.id] == "unlocked"
    assert all(statuses[c.id] == "locked" for c in CHALLENGES[1:])


def test_locked_challenge_cannot_be_viewed_or_submitted(api):
    assert api.get(f"/challenges/{SECOND.id}").status_code == 403
    assert api.post(f"/challenges/{SECOND.id}/hints").status_code == 403
    assert api.submit(SECOND.id, SECOND.reference_sql).status_code == 403


def test_unknown_challenge_is_404(api):
    assert api.get("/challenges/nope").status_code == 404


def test_correct_query_passes_and_unlocks_next(api):
    response = api.submit(
        FIRST.id, "SELECT first_name, last_name, email FROM customers")
    body = response.json()

    assert response.status_code == 200
    assert body["passed"] is True
    assert body["newly_completed"] is True
    assert body["next_challenge_id"] == SECOND.id
    assert body["result"]["columns"] == ["first_name", "last_name", "email"]
    assert api.statuses()[FIRST.id] == "completed"
    assert api.statuses()[SECOND.id] == "unlocked"


def test_equivalent_query_passes(api):
    sql = "select c.first_name as fn, c.last_name, c.email from customers c where 1 = 1 order by c.email"
    assert api.submit(FIRST.id, sql).json()["passed"] is True


def test_incorrect_result_fails_without_unlocking(api):
    body = api.submit(
        FIRST.id, "SELECT first_name, last_name, email FROM customers WHERE city = 'London'").json()

    assert body["passed"] is False
    assert body["code"] == "row_count"
    assert body["next_challenge_id"] is None
    assert api.statuses()[SECOND.id] == "locked"


def test_ordering_is_enforced_when_required(api):
    api.submit(FIRST.id, FIRST.reference_sql)
    body = api.submit(
        SECOND.id, "SELECT name, price FROM products WHERE price > 50 ORDER BY price").json()
    assert body["passed"] is False
    assert body["code"] == "row_order"


def test_completed_challenge_can_be_rerun(api):
    api.submit(FIRST.id, FIRST.reference_sql)
    body = api.submit(FIRST.id, FIRST.reference_sql).json()
    assert body["passed"] is True
    assert body["newly_completed"] is False


@pytest.mark.parametrize("sql", ["DROP TABLE customers", "INSERT INTO categories (name) VALUES ('x')", "COMMIT",
                                 "SELECT * FROM _app_progress"])
def test_blocked_sql_via_api(api, sql):
    body = api.submit(FIRST.id, sql).json()
    assert body["passed"] is False
    assert body["code"] == "not_allowed"
    assert api.get("/learner/schema").status_code == 200
    assert api.submit(FIRST.id, FIRST.reference_sql).json()["passed"] is True


def test_hints_are_revealed_progressively(api):
    assert api.get(f"/challenges/{FIRST.id}").json()["hints"] == []
    for count in range(1, len(FIRST.hints) + 2):
        body = api.post(f"/challenges/{FIRST.id}/hints").json()
        assert body["hints"] == FIRST.hints[: min(count, len(FIRST.hints))]
        assert body["total_hints"] == len(FIRST.hints)
    assert api.get(f"/challenges/{FIRST.id}").json()["hints"] == FIRST.hints


def test_reset_clears_progress_and_hints(api):
    api.submit(FIRST.id, FIRST.reference_sql)
    api.post(f"/challenges/{FIRST.id}/hints")
    api.post("/learner/reset")
    assert api.statuses()[SECOND.id] == "locked"
    assert api.get(f"/challenges/{FIRST.id}").json()["hints"] == []


def _normalise(sql: str) -> str:
    return " ".join(sql.split()).rstrip(";").lower()


def test_reference_sql_never_appears_in_responses(api):
    responses = [
        api.get("/challenges"),
        api.get(f"/challenges/{FIRST.id}"),
        api.submit(FIRST.id, "SELECT 1, 2, 3"),
        api.submit(FIRST.id, "SELECT first_name FROM customers"),
        api.submit(FIRST.id, "nonsense"),
        api.submit(FIRST.id, FIRST.reference_sql),
        api.get(f"/challenges/{SECOND.id}"),
        api.submit(SECOND.id, "SELECT name, price FROM products"),
        api.submit(
            SECOND.id, "SELECT name, price FROM products WHERE price > 50"),
        api.get(f"/challenges/{SECOND.id}"),
    ]
    for _ in SECOND.hints:
        responses.append(api.post(f"/challenges/{SECOND.id}/hints"))

    references = [_normalise(c.reference_sql) for c in CHALLENGES]
    for response in responses:
        text = _normalise(json.dumps(response.json()))
        assert "reference" not in text
        for reference in references:
            assert reference not in text
