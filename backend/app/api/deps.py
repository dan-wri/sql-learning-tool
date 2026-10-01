from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from app.learners.store import InvalidLearnerId, LearnerStore, parse_learner_id


def get_store(request: Request) -> LearnerStore:
    return request.app.state.learner_store


def get_learner_id(x_learner_id: Annotated[str, Header()]) -> str:
    try:
        return parse_learner_id(x_learner_id)
    except InvalidLearnerId as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


StoreDep = Annotated[LearnerStore, Depends(get_store)]
LearnerIdDep = Annotated[str, Depends(get_learner_id)]
