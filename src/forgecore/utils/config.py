"""Application settings loaded from YAML + environment variables.

Order of precedence (highest wins):
  1. Environment variables
  2. .env file (loaded via pydantic-settings)
  3. config/settings.yaml
  4. Pydantic defaults

This lets us keep tunables (chunk size, model name, top-k) in YAML while
keeping secrets (API keys) in environment variables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from forgecore.utils.paths import ENV_FILE, SETTINGS_FILE


# ─── Nested config models ─────────────────────────────────────
class PathsConfig(BaseModel):
    """Where data, configs, and the vector DB live."""

    raw_docs_dir: str = "./data/raw"
    processed_dir: str = "./data/processed"
    eval_dir: str = "./data/eval"
    vector_db_dir: str = "./chroma_db"


class ChunkingConfig(BaseModel):
    """How documents are split into chunks."""

    chunk_size: int = Field(default=500, ge=100, le=4000)
    chunk_overlap: int = Field(default=50, ge=0, le=1000)
    splitter_separators: list[str] = Field(
        default_factory=lambda: ["\n\n", "\n", ". ", " ", ""]
    )


class EmbeddingsConfig(BaseModel):
    """Embedding model selection."""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32
    device: str = "cpu"  # Codespaces has no GPU; "cuda" if you have one


class RetrievalConfig(BaseModel):
    """Vector search parameters."""

    top_k: int = Field(default=5, ge=1, le=50)
    distance_metric: str = "cosine"
    collection_name: str = "forgecore_knowledge"


class LLMConfig(BaseModel):
    """LLM provider settings."""

    provider: str = "gemini"
    model: str = "gemini-2.0-flash"
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    max_output_tokens: int = Field(default=1024, ge=64, le=8192)


class AppConfig(BaseModel):
    """Top-level application settings."""

    env: str = "development"
    log_level: str = "INFO"
    paths: PathsConfig = Field(default_factory=PathsConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)


# ─── Loader ───────────────────────────────────────────────────
class Settings(BaseSettings):
    """Top-level settings sourced from .env + YAML."""

    # Secrets / per-deploy values come from .env
    gemini_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def app(self) -> AppConfig:
        """Load (and cache) the YAML-backed AppConfig."""
        if not hasattr(self, "_cached_app"):
            self._cached_app = _load_yaml_config()
        return self._cached_app  # type: ignore[attr-defined]


def _load_yaml_config(path: Path = SETTINGS_FILE) -> AppConfig:
    """Read settings.yaml and merge with the bundled defaults."""
    if not path.exists():
        return AppConfig()

    with path.open("r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh) or {}

    # Map top-level YAML keys onto AppConfig fields.
    return AppConfig(**raw)


def get_settings() -> Settings:
    """Convenience accessor — call this anywhere you need settings."""
    return Settings()
