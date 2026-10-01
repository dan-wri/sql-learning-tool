import math

from fastapi import APIRouter, HTTPException, Request

from app.api.deps import LearnerIdDep, StoreDep
from app.challenges.registry import Challenge, ChallengeRegistry
from app.progress.service import completed_ids, hints_revealed, reveal_next_hint, status_of
from app.schemas import (
    ChallengeDetail,
    ChallengeSummary,
    ChangeCounts,
    HintsResponse,
    ResultPayload,
    RowUpdate,
    SubmitRequest,
    SubmitResponse,
    TableChangesPayload,
)
from app.sql.executor import QueryResult
from app.sql.orchestrator import submit
from app.sql.sandbox import review_sandbox_factory
from app.sql.snapshot import TableChanges

router = APIRouter(prefix="/challenges", tags=["challenges"])

MAX_PREVIEW_ROWS = 50


def _registry(request: Request) -> ChallengeRegistry:
    return request.app.state.registry


def _unlocked_challenge(registry: ChallengeRegistry, completed: set[str], challenge_id: str) -> Challenge:
    challenge = registry.get(challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if status_of(registry, completed, challenge_id) == "locked":
        raise HTTPException(
            status_code=403, detail="Complete the previous challenge to unlock this one")
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


def _row(row: tuple) -> list:
    return [_jsonable(v) for v in row]


def _changes_payload(changes: dict[str, TableChanges] | None) -> list[TableChangesPayload] | None:
    if changes is None:
        return None
    return [
        TableChangesPayload(
            table=c.table,
            columns=c.columns,
            inserted=[_row(r) for r in c.inserted[:MAX_PREVIEW_ROWS]],
            updated=[RowUpdate(before=_row(b), after=_row(a)) for b, a in c.updated[:MAX_PREVIEW_ROWS]],
            deleted=[_row(r) for r in c.deleted[:MAX_PREVIEW_ROWS]],
            counts=ChangeCounts(inserted=len(c.inserted), updated=len(c.updated), deleted=len(c.deleted)),
        )
        for c in changes.values()
    ]


@router.get("", response_model=list[ChallengeSummary])
def list_challenges(request: Request, store: StoreDep, learner_id: LearnerIdDep) -> list[ChallengeSummary]:
    registry = _registry(request)
    with store.connection(learner_id) as conn:
        completed = completed_ids(conn)
    return [
        ChallengeSummary(id=c.id, title=c.title, difficulty=c.difficulty, kind=c.kind,
                         status=status_of(registry, completed, c.id))
        for c in registry.all()
    ]


@router.get("/{challenge_id}", response_model=ChallengeDetail)
def get_challenge(challenge_id: str, request: Request, store: StoreDep, learner_id: LearnerIdDep) -> ChallengeDetail:
    registry = _registry(request)
    with store.connection(learner_id) as conn:
        completed = completed_ids(conn)
        challenge = _unlocked_challenge(registry, completed, challenge_id)
        revealed = hints_revealed(conn, challenge_id)
    status = status_of(registry, completed, challenge_id)
    return ChallengeDetail(
        id=challenge.id,
        title=challenge.title,
        difficulty=challenge.difficulty,
        kind=challenge.kind,
        status=status,
        instructions=challenge.instructions,
        hints=challenge.hints[:revealed],
        total_hints=len(challenge.hints),
        review_mode=challenge.kind == "mutation" and status == "completed",
    )


@router.post("/{challenge_id}/hints", response_model=HintsResponse)
def reveal_hint(challenge_id: str, request: Request, store: StoreDep, learner_id: LearnerIdDep) -> HintsResponse:
    registry = _registry(request)
    with store.connection(learner_id) as conn:
        challenge = _unlocked_challenge(
            registry, completed_ids(conn), challenge_id)
        revealed = reveal_next_hint(conn, challenge_id, len(challenge.hints))
    return HintsResponse(hints=challenge.hints[:revealed], total_hints=len(challenge.hints))


@router.post("/{challenge_id}/submit", response_model=SubmitResponse)
def submit_solution(challenge_id: str, body: SubmitRequest, request: Request, store: StoreDep,
                    learner_id: LearnerIdDep) -> SubmitResponse:
    registry = _registry(request)
    with store.connection(learner_id) as conn:
        challenge = _unlocked_challenge(
            registry, completed_ids(conn), challenge_id)
        sandbox = review_sandbox_factory(store.template_path, registry.all(), challenge_id)
        outcome = submit(conn, challenge, body.sql, review_sandbox=sandbox)
    next_challenge = registry.next(challenge_id) if outcome.passed else None
    return SubmitResponse(
        passed=outcome.passed,
        code=outcome.code,
        message=outcome.message,
        result=_payload(outcome.result),
        changes=_changes_payload(outcome.changes),
        persisted=outcome.persisted,
        review_mode=outcome.review_mode,
        newly_completed=outcome.newly_completed,
        next_challenge_id=next_challenge.id if next_challenge else None,
    )
