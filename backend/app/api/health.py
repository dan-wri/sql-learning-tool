import sqlite3

from fastapi import APIRouter

from app.db.build_template import SEED_VERSION
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", sqlite_version=sqlite3.sqlite_version, seed_version=SEED_VERSION)
