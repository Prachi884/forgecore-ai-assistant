"""Unit tests for forgecore.utils.config."""

from __future__ import annotations

from forgecore.utils.config import AppConfig, ChunkingConfig, EmbeddingsConfig, get_settings


class TestDefaultConfig:
    def test_get_settings_returns_settings_instance(self) -> None:
        settings = get_settings()
        # `Settings` is a pydantic-settings BaseSettings; .app returns AppConfig
        assert hasattr(settings, "app")
        assert isinstance(settings.app, AppConfig)

    def test_chunking_defaults_are_sensible(self) -> None:
        cfg = ChunkingConfig()
        assert 100 <= cfg.chunk_size <= 4000
        assert 0 <= cfg.chunk_overlap < cfg.chunk_size

    def test_embeddings_defaults_use_minilm(self) -> None:
        cfg = EmbeddingsConfig()
        assert "MiniLM" in cfg.model_name
        assert cfg.dimension > 0


class TestConfigValidation:
    def test_chunk_size_too_small_rejected(self) -> None:
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ChunkingConfig(chunk_size=50)

    def test_overlap_too_large_rejected(self) -> None:
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ChunkingConfig(chunk_size=100, chunk_overlap=2000)
