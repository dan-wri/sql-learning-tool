"""Load challenge definitions from YAML. Challenge order is the sorted file name order."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.sql.authorizer import READ_ONLY, AccessPolicy


class Challenge(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    title: str = Field(min_length=1)
    difficulty: Literal["beginner", "intermediate", "advanced"]
    # "mutation" (INSERT/UPDATE/DELETE validated by state diff) is the next kind to add.
    kind: Literal["query"] = "query"
    instructions: str = Field(min_length=1)
    reference_sql: str = Field(min_length=1)
    ordered: bool = False
    hints: list[str] = Field(min_length=1)
    # Other correct solutions; only used by tests to prove equivalent SQL is accepted.
    accepted_alternatives: list[str] = Field(default_factory=list)

    @property
    def access_policy(self) -> AccessPolicy:
        return READ_ONLY


class ChallengeRegistry:
    def __init__(self, challenges: list[Challenge]):
        self._challenges = list(challenges)
        self._index = {c.id: i for i, c in enumerate(self._challenges)}

    def all(self) -> list[Challenge]:
        return list(self._challenges)

    def get(self, challenge_id: str) -> Challenge | None:
        index = self._index.get(challenge_id)
        return None if index is None else self._challenges[index]

    def previous(self, challenge_id: str) -> Challenge | None:
        index = self._index[challenge_id]
        return self._challenges[index - 1] if index > 0 else None

    def next(self, challenge_id: str) -> Challenge | None:
        index = self._index[challenge_id]
        return self._challenges[index + 1] if index + 1 < len(self._challenges) else None


class ChallengeContentError(ValueError):
    pass


def load_challenges(directory: Path) -> ChallengeRegistry:
    challenges: list[Challenge] = []
    seen: set[str] = set()
    for path in sorted(directory.glob("*.yaml")):
        try:
            challenge = Challenge.model_validate(yaml.safe_load(path.read_text()))
        except (yaml.YAMLError, ValidationError) as exc:
            raise ChallengeContentError(f"{path.name}: {exc}") from exc
        if challenge.id in seen:
            raise ChallengeContentError(f"{path.name}: duplicate challenge id '{challenge.id}'")
        seen.add(challenge.id)
        challenges.append(challenge)
    if not challenges:
        raise ChallengeContentError(f"No challenges found in {directory}")
    return ChallengeRegistry(challenges)
