from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import challenges, health, learner
from app.challenges.registry import load_challenges
from app.config import Settings
from app.db.build_template import ensure_template
from app.learners.store import LearnerStore


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        ensure_template(settings.template_path)
        yield

    app = FastAPI(title="SQL Learning Tool", lifespan=lifespan)
    app.state.settings = settings
    app.state.learner_store = LearnerStore(
        settings.template_path, settings.learners_dir)
    app.state.registry = load_challenges(settings.challenges_dir)

    app.include_router(health.router, prefix="/api")
    app.include_router(learner.router, prefix="/api")
    app.include_router(challenges.router, prefix="/api")
    return app


app = create_app()
