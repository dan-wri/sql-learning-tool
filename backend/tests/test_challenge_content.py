import pytest

from app.challenges.registry import ChallengeContentError, load_challenges
from app.config import CHALLENGES_DIR
from app.sql.orchestrator import submit
from tests.helpers import replay_until, visible_state

REGISTRY = load_challenges(CHALLENGES_DIR)
CHALLENGES = REGISTRY.all()


EXPECTED_BLOCK = [
    ("l01-meet-the-catalogue", "Meet the catalogue"),
    ("l02-first-contact-sheet", "First contact sheet"),
    ("l03-uk-customers", "UK customers"),
    ("l04-budget-finds", "Budget finds"),
    ("l05-ready-to-sell", "Ready to sell"),
    ("l06-products-needing-attention", "Products needing attention"),
    ("l07-price-list", "Price list"),
    ("l08-premium-range", "Premium range"),
    ("l09-top-five-by-stock", "Top five by stock"),
    ("l10-missing-phone-numbers", "Missing phone numbers"),
]
ORDERED_LEVELS = {7, 8, 9}


def test_exactly_levels_one_to_ten_are_active_in_order():
    assert [(c.id, c.title) for c in CHALLENGES] == EXPECTED_BLOCK
    assert [c.level for c in CHALLENGES] == list(range(1, 11))
    assert len({c.id for c in CHALLENGES}) == 10


def test_prototype_challenges_are_not_active():
    ids = {c.id for c in CHALLENGES}
    assert not ids & {"customer-contact-list", "premium-products", "add-new-customer"}
    assert all(c.kind == "query" for c in CHALLENGES)
    assert not any("grace" in c.reference_sql.lower() for c in CHALLENGES)


@pytest.mark.parametrize("challenge", CHALLENGES, ids=lambda c: c.id)
def test_content_metadata_and_hint_ladder(challenge):
    assert challenge.story.strip() and challenge.instructions.strip()
    assert challenge.story.strip() != challenge.instructions.strip()
    assert challenge.chapter == 1
    assert challenge.concepts
    assert len(challenge.hints) == 3
    reference = " ".join(challenge.reference_sql.split()).rstrip(";").lower()
    for hint in challenge.hints:
        assert reference not in " ".join(hint.split()).lower()
    assert challenge.ordered == (challenge.level in ORDERED_LEVELS)


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
story: S
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
        ("write_operations: [INSERT]\nwritable_tables: [customers]\n",
         "query challenges cannot"),
        ("kind: mutation\n", "need write_operations"),
        ("kind: mutation\nwrite_operations: [INSERT]\n",
         "need write_operations"),
        ("kind: mutation\nwrite_operations: [INSERT]\nwritable_tables: [_app_progress]\n", "internal tables"),
        ("kind: mutation\nwrite_operations: [TRUNCATE]\nwritable_tables: [customers]\n",
         "write_operations"),
        ("kind: mutation\nwrite_operations: [INSERT]\nwritable_tables: [customers]\nordered: true\n", "ordered"),
    ],
)
def test_loader_validates_mutation_fields(tmp_path, extra, error):
    _write(tmp_path, "01.yaml", VALID.format(id="a") + extra)
    with pytest.raises(ChallengeContentError, match=error):
        load_challenges(tmp_path)


def test_loader_requires_story(tmp_path):
    _write(tmp_path, "01.yaml", VALID.format(id="a").replace("story: S\n", ""))
    with pytest.raises(ChallengeContentError, match="story"):
        load_challenges(tmp_path)


def test_loader_rejects_level_that_disagrees_with_file_order(tmp_path):
    _write(tmp_path, "01.yaml", VALID.format(id="a") + "level: 2\n")
    with pytest.raises(ChallengeContentError, match="position"):
        load_challenges(tmp_path)


def test_loader_rejects_query_only_options_on_mutations(tmp_path):
    base = VALID.format(id="a") + "kind: mutation\nwrite_operations: [INSERT]\nwritable_tables: [customers]\n"
    for extra in ("match_column_names: true\n", "required_features: [cte]\n"):
        _write(tmp_path, "01.yaml", base + extra)
        with pytest.raises(ChallengeContentError, match="only apply to query"):
            load_challenges(tmp_path)


def test_loader_rejects_unknown_required_feature(tmp_path):
    _write(tmp_path, "01.yaml", VALID.format(id="a") + "required_features: [magic]\n")
    with pytest.raises(ChallengeContentError):
        load_challenges(tmp_path)
