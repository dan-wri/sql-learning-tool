from pydantic import BaseModel


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
