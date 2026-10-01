import json

import pytest

from app.challenges.registry import load_challenges
from app.config import CHALLENGES_DIR

CHALLENGES = load_challenges(CHALLENGES_DIR).all()
INSERT_CHALLENGE = next(c for c in CHALLENGES if c.id == "add-new-customer")
EARLIER = CHALLENGES[: CHALLENGES.index(INSERT_CHALLENGE)]
GRACE_EMAIL = "grace.hopper@example.com"
WRONG_INSERT = ("INSERT INTO customers (first_name, last_name, email, city, country, signup_date) "
                "VALUES ('Grace', 'Hopper', 'grace@example.com', 'Paris', 'UK', '2025-07-01')")


@pytest.fixture
def api(client, learner_id):
    headers = {"X-Learner-Id": learner_id}
    store = client.app.state.learner_store

    class Api:
        def get(self, path):
            return client.get(f"/api{path}", headers=headers)

        def post(self, path, body=None):
            return client.post(f"/api{path}", headers=headers, json=body)

        def submit(self, challenge_id, sql):
            return self.post(f"/challenges/{challenge_id}/submit", {"sql": sql}).json()

        def statuses(self):
            return {c["id"]: c["status"] for c in self.get("/challenges").json()}

        def grace_count(self):
            with store.connection(learner_id) as conn:
                return conn.execute("SELECT COUNT(*) FROM customers WHERE email = ?", (GRACE_EMAIL,)).fetchone()[0]

        def unlock_insert_challenge(self):
            for challenge in EARLIER:
                assert self.submit(challenge.id, challenge.reference_sql)["passed"]

    return Api()


def test_insert_challenge_is_locked_until_earlier_ones_pass(api):
    assert api.get(f"/challenges/{INSERT_CHALLENGE.id}").status_code == 403
    api.unlock_insert_challenge()
    detail = api.get(f"/challenges/{INSERT_CHALLENGE.id}").json()
    assert detail["kind"] == "mutation"
    assert detail["status"] == "unlocked"
    assert detail["review_mode"] is False


def test_incorrect_insert_fails_and_does_not_persist(api):
    api.unlock_insert_challenge()
    body = api.submit(INSERT_CHALLENGE.id, WRONG_INSERT)

    assert body["passed"] is False
    assert body["code"] == "wrong_values"
    assert body["persisted"] is False
    assert body["changes"][0]["table"] == "customers"
    assert body["changes"][0]["counts"] == {"inserted": 1, "updated": 0, "deleted": 0}
    assert "grace@example.com" in body["changes"][0]["inserted"][0]
    assert api.grace_count() == 0
    assert api.statuses()[INSERT_CHALLENGE.id] == "unlocked"


def test_insert_into_wrong_table_is_blocked(api):
    api.unlock_insert_challenge()
    body = api.submit(INSERT_CHALLENGE.id, "INSERT INTO categories (name) VALUES ('Garden')")
    assert body["passed"] is False
    assert body["code"] == "not_allowed"
    assert body["changes"] is None


def test_correct_insert_persists_and_is_visible_to_later_queries(api):
    api.unlock_insert_challenge()
    body = api.submit(INSERT_CHALLENGE.id, INSERT_CHALLENGE.reference_sql)

    assert body["passed"] is True
    assert body["persisted"] is True
    assert body["review_mode"] is False
    assert body["newly_completed"] is True
    (table,) = body["changes"]
    assert table["columns"][0] == "customer_id"
    assert table["inserted"][0][1:4] == ["Grace", "Hopper", GRACE_EMAIL]
    assert api.grace_count() == 1
    assert api.statuses()[INSERT_CHALLENGE.id] == "completed"

    contact_list = api.submit(CHALLENGES[0].id, "SELECT first_name, last_name, email FROM customers")
    assert contact_list["passed"] is True
    assert ["Grace", "Hopper", GRACE_EMAIL] in contact_list["result"]["rows"]


def test_completed_insert_runs_in_review_mode(api):
    api.unlock_insert_challenge()
    api.submit(INSERT_CHALLENGE.id, INSERT_CHALLENGE.reference_sql)

    detail = api.get(f"/challenges/{INSERT_CHALLENGE.id}").json()
    assert detail["review_mode"] is True

    replay = api.submit(INSERT_CHALLENGE.id, INSERT_CHALLENGE.reference_sql)
    assert replay["passed"] is True
    assert replay["review_mode"] is True
    assert replay["persisted"] is False
    assert replay["changes"][0]["counts"]["inserted"] == 1

    wrong = api.submit(INSERT_CHALLENGE.id, WRONG_INSERT)
    assert wrong["passed"] is False
    assert wrong["review_mode"] is True
    assert "email" in wrong["message"]

    assert api.post(f"/challenges/{INSERT_CHALLENGE.id}/hints").json()["hints"] == INSERT_CHALLENGE.hints[:1]
    assert api.grace_count() == 1
    assert api.statuses()[INSERT_CHALLENGE.id] == "completed"


def test_reset_removes_inserted_customer_and_progress(api):
    api.unlock_insert_challenge()
    api.submit(INSERT_CHALLENGE.id, INSERT_CHALLENGE.reference_sql)

    api.post("/learner/reset")

    assert api.grace_count() == 0
    statuses = api.statuses()
    assert statuses[CHALLENGES[0].id] == "unlocked"
    assert statuses[INSERT_CHALLENGE.id] == "locked"


def test_reference_sql_never_appears_in_mutation_responses(api):
    api.unlock_insert_challenge()
    responses = [
        api.get(f"/challenges/{INSERT_CHALLENGE.id}").json(),
        api.submit(INSERT_CHALLENGE.id, WRONG_INSERT),
        api.submit(INSERT_CHALLENGE.id, "SELECT * FROM customers"),
        api.submit(INSERT_CHALLENGE.id, "DELETE FROM customers"),
        api.submit(INSERT_CHALLENGE.id, INSERT_CHALLENGE.reference_sql),
        api.submit(INSERT_CHALLENGE.id, WRONG_INSERT),
        api.get(f"/challenges/{INSERT_CHALLENGE.id}").json(),
    ]
    reference = " ".join(INSERT_CHALLENGE.reference_sql.split()).rstrip(";").lower()
    for body in responses:
        text = " ".join(json.dumps(body).split()).lower()
        assert reference not in text
        assert "reference" not in text
