"""The learning path: replay every reference solution in order on one database, as a learner would."""

from app.challenges.registry import load_challenges
from app.config import CHALLENGES_DIR
from app.progress.service import completed_ids, status_of
from app.sql.orchestrator import submit
from app.sql.sandbox import review_sandbox_factory
from tests.helpers import internal_state, visible_state

REGISTRY = load_challenges(CHALLENGES_DIR)
CHALLENGES = REGISTRY.all()


def _statuses(conn):
    completed = completed_ids(conn)
    return [status_of(REGISTRY, completed, c.id) for c in CHALLENGES]


def test_block_can_be_completed_in_order_and_unlocks_sequentially(store, learner_id):
    with store.connection(learner_id) as conn:
        initial_data = visible_state(conn)
        assert _statuses(conn) == ["unlocked"] + ["locked"] * 9

        for position, challenge in enumerate(CHALLENGES):
            assert _statuses(conn)[position] == "unlocked"
            outcome = submit(conn, challenge, challenge.reference_sql)
            assert outcome.passed, f"{challenge.id}: {outcome.message}"
            assert outcome.persisted and outcome.newly_completed and not outcome.review_mode

            expected = ["completed"] * (position + 1)
            expected += ["unlocked"] if position + 1 < len(CHALLENGES) else []
            expected += ["locked"] * (len(CHALLENGES) - len(expected))
            assert _statuses(conn) == expected
            assert completed_ids(conn) == {c.id for c in CHALLENGES[: position + 1]}
            # Query-only block: business data is untouched throughout.
            assert visible_state(conn) == initial_data

        assert _statuses(conn) == ["completed"] * 10
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute("PRAGMA integrity_check").fetchone() == ("ok",)


def test_completed_levels_replay_in_review_mode_without_changing_anything(store, learner_id):
    with store.connection(learner_id) as conn:
        for challenge in CHALLENGES:
            assert submit(conn, challenge, challenge.reference_sql).passed
        final_state = visible_state(conn), internal_state(conn)

        for challenge in CHALLENGES:
            sandbox = review_sandbox_factory(store.template_path, CHALLENGES, challenge.id)
            outcome = submit(conn, challenge, challenge.reference_sql, review_sandbox=sandbox)
            assert outcome.passed, f"{challenge.id} no longer passes in review: {outcome.message}"
            assert outcome.review_mode and not outcome.persisted and not outcome.newly_completed
        assert (visible_state(conn), internal_state(conn)) == final_state


def test_reset_restores_the_initial_state(store, learner_id):
    with store.connection(learner_id) as conn:
        for challenge in CHALLENGES[:4]:
            assert submit(conn, challenge, challenge.reference_sql).passed
    store.reset(learner_id)
    with store.connection(learner_id) as conn:
        assert _statuses(conn) == ["unlocked"] + ["locked"] * 9
        assert conn.execute("SELECT COUNT(*) FROM _app_hints").fetchone() == (0,)
