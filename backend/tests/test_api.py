import uuid


def _headers(learner_id: str) -> dict[str, str]:
    return {"X-Learner-Id": learner_id}


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["sqlite_version"]


def test_session_creates_learner_db_then_reuses_it(client, learner_id):
    first = client.post("/api/learner/session", headers=_headers(learner_id))
    second = client.post("/api/learner/session", headers=_headers(learner_id))

    assert first.status_code == 200
    assert first.json()["created"] is True
    assert first.json()["stale"] is False
    assert second.json()["created"] is False


def test_invalid_learner_id_is_rejected(client):
    response = client.post("/api/learner/session", headers=_headers("../../template"))
    assert response.status_code == 400


def test_missing_learner_id_is_rejected(client):
    assert client.post("/api/learner/session").status_code == 422


def test_schema_hides_internal_tables(client, learner_id):
    response = client.get("/api/learner/schema", headers=_headers(learner_id))
    assert response.status_code == 200
    names = [t["name"] for t in response.json()["tables"]]
    assert "customers" in names
    assert not any(n.startswith("_app_") or n.startswith("sqlite_") for n in names)


def test_reset_endpoint(client, settings):
    learner_id = str(uuid.uuid4())
    client.post("/api/learner/session", headers=_headers(learner_id))

    response = client.post("/api/learner/reset", headers=_headers(learner_id))

    assert response.status_code == 200
    assert response.json()["learner_id"] == learner_id
    assert (settings.learners_dir / f"{learner_id}.db").exists()
