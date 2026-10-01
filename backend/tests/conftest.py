import uuid

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.build_template import build_template
from app.learners.store import LearnerStore
from app.main import create_app


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(data_dir=tmp_path / "data")


@pytest.fixture
def template(settings) -> Settings:
    build_template(settings.template_path)
    return settings


@pytest.fixture
def store(template) -> LearnerStore:
    return LearnerStore(template.template_path, template.learners_dir)


@pytest.fixture
def learner_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as test_client:
        yield test_client
