import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    data_dir: Path

    @property
    def template_path(self) -> Path:
        return self.data_dir / "template.db"

    @property
    def learners_dir(self) -> Path:
        return self.data_dir / "learners"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(data_dir=Path(os.environ.get("SQL_TOOL_DATA_DIR", BACKEND_DIR / "data")))
