"""The learning path depends on earlier mutations: replay every reference solution in order on one database."""

from app.challenges.registry import load_challenges
from app.config import CHALLENGES_DIR
from app.progress.service import completed_ids
from app.sql.orchestrator import submit
from app.sql.sandbox import review_sandbox_factory
from tests.helpers import internal_state, visible_state

CHALLENGES = load_challenges(CHALLENGES_DIR).all()


def test_reference_chain_replays_cleanly_and_stays_valid(store, learner_id):
    with store.connection(learner_id) as conn:
        for challenge in CHALLENGES:
            outcome = submit(conn, challenge, challenge.reference_sql)
            assert outcome.passed, f"{challenge.id}: {outcome.message}"
            assert outcome.persisted
            assert outcome.newly_completed
        assert completed_ids(conn) == {c.id for c in CHALLENGES}

        final_state = visible_state(conn), internal_state(conn)
        for challenge in CHALLENGES:
            sandbox = review_sandbox_factory(store.template_path, CHALLENGES, challenge.id)
            outcome = submit(conn, challenge, challenge.reference_sql, review_sandbox=sandbox)
            assert outcome.passed, f"{challenge.id} no longer passes on the evolved database: {outcome.message}"
            assert outcome.review_mode == (challenge.kind == "mutation")
            assert not outcome.newly_completed
        assert (visible_state(conn), internal_state(conn)) == final_state


def test_committed_insert_is_visible_to_later_selects(store, learner_id):
    contact_list = CHALLENGES[0]
    with store.connection(learner_id) as conn:
        before = submit(conn, contact_list, contact_list.reference_sql).result.rows
        for challenge in CHALLENGES:
            submit(conn, challenge, challenge.reference_sql)
        after = submit(conn, contact_list, "SELECT first_name, last_name, email FROM customers").result.rows

    assert len(after) == len(before) + 1
    assert ("Grace", "Hopper", "grace.hopper@example.com") in after
