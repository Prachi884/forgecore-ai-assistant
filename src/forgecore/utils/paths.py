"""Project-relative paths, resolved from the repo root.

Centralising paths means every module agrees on where data, configs, and the
vector DB live — no hardcoded `'./data/raw'` strings scattered through the code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final


def find_project_root(start: Path | None = None) -> Path:
    """Walk upward from `start` (default: this file) until we find a pyproject.toml.

    This makes the package work whether you run it from the repo root,
    from inside `src/forgecore/`, or from a CI runner.
    """
    current = (start or Path(__file__).resolve()).parent
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    # Fallback: assume CWD is the project root.
    return Path.cwd().resolve()


# Resolve once at import time.
PROJECT_ROOT: Final[Path] = find_project_root()

# ─── Directory layout ─────────────────────────────────────────
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
RAW_DOCS_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DIR: Final[Path] = DATA_DIR / "processed"
EVAL_DIR: Final[Path] = DATA_DIR / "eval"

CONFIG_DIR: Final[Path] = PROJECT_ROOT / "config"
SETTINGS_FILE: Final[Path] = CONFIG_DIR / "settings.yaml"

VECTOR_DB_DIR: Final[Path] = PROJECT_ROOT / "chroma_db"

NOTEBOOKS_DIR: Final[Path] = PROJECT_ROOT / "notebooks"
DOCS_DIR: Final[Path] = PROJECT_ROOT / "docs"
LOGS_DIR: Final[Path] = PROJECT_ROOT / "logs"

# ─── Standard files ───────────────────────────────────────────
ENV_FILE: Final[Path] = PROJECT_ROOT / ".env"
GITIGNORE_FILE: Final[Path] = PROJECT_ROOT / ".gitignore"


def ensure_directory(path: Path) -> Path:
    """Create `path` (including parents) if it doesn't exist, then return it.

    Idempotent — safe to call repeatedly.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
