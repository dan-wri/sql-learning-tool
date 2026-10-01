from typing import Any, Literal

from pydantic import BaseModel, Field

from app.sql.executor import MAX_SQL_LENGTH

ChallengeStatus = Literal["completed", "unlocked", "locked"]


class ChallengeSummary(BaseModel):
    id: str
    title: str
    difficulty: str
    status: ChallengeStatus


class ChallengeDetail(ChallengeSummary):
    instructions: str
    hints: list[str]
    total_hints: int


class HintsResponse(BaseModel):
    hints: list[str]
    total_hints: int


class SubmitRequest(BaseModel):
    # Generous hard cap on the body; the executor gives the friendly length error.
    sql: str = Field(max_length=MAX_SQL_LENGTH * 2)


class ResultPayload(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    truncated: bool


class SubmitResponse(BaseModel):
    passed: bool
    code: str
    message: str
    result: ResultPayload | None
    newly_completed: bool
    next_challenge_id: str | None


class HealthResponse(BaseModel):
    status: str
    sqlite_version: str
    seed_version: int


class LearnerSession(BaseModel):
    learner_id: str
    created: bool
    seed_version: int | None
    current_seed_version: int
    stale: bool


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool


class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]


class SchemaResponse(BaseModel):
    tables: list[TableInfo]
