import math

from fastapi import APIRouter, HTTPException, Request

from app.api.deps import LearnerIdDep, StoreDep
from app.challenges.registry import Challenge, ChallengeRegistry
from app.progress.service import completed_ids, hints_revealed, reveal_next_hint, status_of
from app.schemas import (
    ChallengeDetail,
    ChallengeSummary,
    HintsResponse,
    ResultPayload,
    SubmitRequest,
    SubmitResponse,
)
from app.sql.executor import QueryResult
from app.sql.orchestrator import submit

router = APIRouter(prefix="/challenges", tags=["challenges"])


def _registry(request: Request) -> ChallengeRegistry:
    return request.app.state.registry


def _unlocked_challenge(registry: ChallengeRegistry, completed: set[str], challenge_id: str) -> Challenge:
    challenge = registry.get(challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if status_of(registry, completed, challenge_id) == "locked":
        raise HTTPException(status_code=403, detail="Complete the previous challenge to unlock this one")
    return challenge


def _jsonable(value):
    if isinstance(value, bytes):
        return f"<blob: {len(value)} bytes>"
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def _payload(result: QueryResult | None) -> ResultPayload | None:
    if result is None:
        return None
    rows = [[_jsonable(v) for v in row] for row in result.rows]
    return ResultPayload(columns=result.columns, rows=rows, truncated=result.truncated)


@router.get("", response_model=list[ChallengeSummary])
def list_challenges(request: Request, store: StoreDep, learner_id: LearnerIdDep) -> list[ChallengeSummary]:
    registry = _registry(request)
    with store.connection(learner_id) as conn:
        completed = completed_ids(conn)
    return [
        ChallengeSummary(id=c.id, title=c.title, difficulty=c.difficulty, status=status_of(registry, completed, c.id))
        for c in registry.all()
    ]


@router.get("/{challenge_id}", response_model=ChallengeDetail)
def get_challenge(challenge_id: str, request: Request, store: StoreDep, learner_id: LearnerIdDep) -> ChallengeDetail:
    registry = _registry(request)
    with store.connection(learner_id) as conn:
        completed = completed_ids(conn)
        challenge = _unlocked_challenge(registry, completed, challenge_id)
        revealed = hints_revealed(conn, challenge_id)
    return ChallengeDetail(
        id=challenge.id,
        title=challenge.title,
        difficulty=challenge.difficulty,
        status=status_of(registry, completed, challenge_id),
        instructions=challenge.instructions,
        hints=challenge.hints[:revealed],
        total_hints=len(challenge.hints),
    )


@router.post("/{challenge_id}/hints", response_model=HintsResponse)
def reveal_hint(challenge_id: str, request: Request, store: StoreDep, learner_id: LearnerIdDep) -> HintsResponse:
    registry = _registry(request)
    with store.connection(learner_id) as conn:
        challenge = _unlocked_challenge(registry, completed_ids(conn), challenge_id)
        revealed = reveal_next_hint(conn, challenge_id, len(challenge.hints))
    return HintsResponse(hints=challenge.hints[:revealed], total_hints=len(challenge.hints))


@router.post("/{challenge_id}/submit", response_model=SubmitResponse)
def submit_solution(challenge_id: str, body: SubmitRequest, request: Request, store: StoreDep,
                    learner_id: LearnerIdDep) -> SubmitResponse:
    registry = _registry(request)
    with store.connection(learner_id) as conn:
        challenge = _unlocked_challenge(registry, completed_ids(conn), challenge_id)
        outcome = submit(conn, challenge, body.sql)
    next_challenge = registry.next(challenge_id) if outcome.passed else None
    return SubmitResponse(
        passed=outcome.passed,
        code=outcome.code,
        message=outcome.message,
        result=_payload(outcome.result),
        newly_completed=outcome.newly_completed,
        next_challenge_id=next_challenge.id if next_challenge else None,
    )
