import pytest

from app.challenges.registry import ChallengeContentError, load_challenges
from app.config import CHALLENGES_DIR
from app.sql.orchestrator import submit
from tests.helpers import replay_until, visible_state

REGISTRY = load_challenges(CHALLENGES_DIR)
CHALLENGES = REGISTRY.all()


def test_content_loads_in_file_order():
    assert [c.id for c in CHALLENGES][:3] == [
        "customer-contact-list", "premium-products", "add-new-customer"]


@pytest.mark.parametrize("challenge", CHALLENGES, ids=lambda c: c.id)
def test_reference_solution_passes(store, learner_id, challenge):
    with store.connection(learner_id) as conn:
        replay_until(conn, CHALLENGES, challenge.id)
        before = visible_state(conn)
        outcome = submit(conn, challenge, challenge.reference_sql)
        assert outcome.passed, outcome.message
        if challenge.kind == "query":
            assert outcome.result.rows, "reference result should not be empty"
            assert not outcome.result.truncated
            assert visible_state(conn) == before
        else:
            assert outcome.changes, "reference mutation should change something"
            assert set(outcome.changes) <= set(challenge.writable_tables)
            assert visible_state(conn) != before


@pytest.mark.parametrize(
    "challenge, sql",
    [(c, alt) for c in CHALLENGES for alt in c.accepted_alternatives],
    ids=lambda v: getattr(v, "id", None) or v[:40],
)
def test_accepted_alternatives_pass(store, learner_id, challenge, sql):
    with store.connection(learner_id) as conn:
        replay_until(conn, CHALLENGES, challenge.id)
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
    _write(tmp_path, "01.yaml", VALID.format(
        id="a").replace("hints: [h]", "hints: []"))
    with pytest.raises(ChallengeContentError):
        load_challenges(tmp_path)


def test_loader_rejects_empty_directory(tmp_path):
    with pytest.raises(ChallengeContentError):
        load_challenges(tmp_path)


@pytest.mark.parametrize(
    "extra, error",
    [
        ("write_operations: [INSERT]\nwritable_tables: [customers]\n", "query challenges cannot"),
        ("kind: mutation\n", "need write_operations"),
        ("kind: mutation\nwrite_operations: [INSERT]\n", "need write_operations"),
        ("kind: mutation\nwrite_operations: [INSERT]\nwritable_tables: [_app_progress]\n", "internal tables"),
        ("kind: mutation\nwrite_operations: [TRUNCATE]\nwritable_tables: [customers]\n", "write_operations"),
        ("kind: mutation\nwrite_operations: [INSERT]\nwritable_tables: [customers]\nordered: true\n", "ordered"),
    ],
)
def test_loader_validates_mutation_fields(tmp_path, extra, error):
    _write(tmp_path, "01.yaml", VALID.format(id="a") + extra)
    with pytest.raises(ChallengeContentError, match=error):
        load_challenges(tmp_path)
