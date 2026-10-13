from fastapi import APIRouter

from app.api.deps import LearnerIdDep, StoreDep
from app.db.build_template import SEED_VERSION, read_seed_version
from app.learners.store import LearnerStore
from app.schemas import ColumnInfo, ForeignKeyRef, LearnerSession, SchemaResponse, TableInfo
from app.sql.snapshot import quote_identifier, visible_tables

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
        tables = []
        for name in visible_tables(conn):
            quoted = quote_identifier(name)
            references = {
                fk[3]: ForeignKeyRef(table=fk[2], column=fk[4])
                for fk in conn.execute(f"PRAGMA foreign_key_list({quoted})")
            }
            columns = [
                ColumnInfo(name=col[1], type=col[2], nullable=not (
                    col[3] or col[5]), primary_key=bool(col[5]), references=references.get(col[1]))
                for col in conn.execute(f"PRAGMA table_info({quoted})")
            ]
            row_count = conn.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
            tables.append(TableInfo(name=name, row_count=row_count, columns=columns))
    return SchemaResponse(tables=tables)
