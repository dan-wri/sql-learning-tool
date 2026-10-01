import pytest

from app.challenges.registry import ChallengeContentError, load_challenges
from app.config import CHALLENGES_DIR
from app.sql.orchestrator import submit
from tests.helpers import visible_state

REGISTRY = load_challenges(CHALLENGES_DIR)
CHALLENGES = REGISTRY.all()


def test_content_loads_in_file_order():
    assert [c.id for c in CHALLENGES][:2] == ["customer-contact-list", "premium-products"]


@pytest.mark.parametrize("challenge", CHALLENGES, ids=lambda c: c.id)
def test_reference_solution_passes_and_changes_nothing(store, learner_id, challenge):
    with store.connection(learner_id) as conn:
        before = visible_state(conn)
        outcome = submit(conn, challenge, challenge.reference_sql)
        assert outcome.passed, outcome.message
        assert outcome.result.rows, "reference result should not be empty"
        assert not outcome.result.truncated
        assert visible_state(conn) == before


@pytest.mark.parametrize(
    "challenge, sql",
    [(c, alt) for c in CHALLENGES for alt in c.accepted_alternatives],
    ids=lambda v: getattr(v, "id", None) or v[:40],
)
def test_accepted_alternatives_pass(store, learner_id, challenge, sql):
    with store.connection(learner_id) as conn:
        outcome = submit(conn, challenge, sql)
    assert outcome.passed, outcome.message


def _write(tmp_path, name, text):
    (tmp_path / name).write_text(text)


VALID = """
id: {id}
title: T
difficulty: beginner
instructions: Do it
reference_sql: SELECT 1
hints: [h]
"""


def test_loader_rejects_unknown_fields(tmp_path):
    _write(tmp_path, "01.yaml", VALID.format(id="a") + "refrence_sql: typo\n")
    with pytest.raises(ChallengeContentError, match="01.yaml"):
        load_challenges(tmp_path)


def test_loader_rejects_duplicate_ids(tmp_path):
    _write(tmp_path, "01.yaml", VALID.format(id="a"))
    _write(tmp_path, "02.yaml", VALID.format(id="a"))
    with pytest.raises(ChallengeContentError, match="duplicate"):
        load_challenges(tmp_path)


def test_loader_requires_hints(tmp_path):
    _write(tmp_path, "01.yaml", VALID.format(id="a").replace("hints: [h]", "hints: []"))
    with pytest.raises(ChallengeContentError):
        load_challenges(tmp_path)


def test_loader_rejects_empty_directory(tmp_path):
    with pytest.raises(ChallengeContentError):
        load_challenges(tmp_path)
