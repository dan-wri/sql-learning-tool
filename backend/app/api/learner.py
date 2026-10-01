from fastapi import APIRouter

from app.api.deps import LearnerIdDep, StoreDep
from app.db.build_template import SEED_VERSION, read_seed_version
from app.learners.store import LearnerStore
from app.schemas import ColumnInfo, LearnerSession, SchemaResponse, TableInfo

router = APIRouter(prefix="/learner", tags=["learner"])


def _session(store: LearnerStore, learner_id: str, created: bool) -> LearnerSession:
    with store.connection(learner_id) as conn:
        version = read_seed_version(conn)
    return LearnerSession(
        learner_id=learner_id,
        created=created,
        seed_version=version,
        current_seed_version=SEED_VERSION,
        stale=version != SEED_VERSION,
    )


@router.post("/session", response_model=LearnerSession)
def start_session(store: StoreDep, learner_id: LearnerIdDep) -> LearnerSession:
    created = store.ensure(learner_id)
    return _session(store, learner_id, created)


@router.post("/reset", response_model=LearnerSession)
def reset(store: StoreDep, learner_id: LearnerIdDep) -> LearnerSession:
    store.reset(learner_id)
    return _session(store, learner_id, created=True)


@router.get("/schema", response_model=SchemaResponse)
def schema(store: StoreDep, learner_id: LearnerIdDep) -> SchemaResponse:
    with store.connection(learner_id) as conn:
        names = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_schema WHERE type = 'table' "
                "AND name NOT LIKE '\\_app\\_%' ESCAPE '\\' AND name NOT LIKE 'sqlite\\_%' ESCAPE '\\' "
                "ORDER BY name"
            )
        ]
        tables = []
        for name in names:
            quoted = '"' + name.replace('"', '""') + '"'
            columns = [
                ColumnInfo(name=col[1], type=col[2], nullable=not (col[3] or col[5]), primary_key=bool(col[5]))
                for col in conn.execute(f"PRAGMA table_info({quoted})")
            ]
            tables.append(TableInfo(name=name, columns=columns))
    return SchemaResponse(tables=tables)
