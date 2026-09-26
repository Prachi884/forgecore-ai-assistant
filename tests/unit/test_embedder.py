"""Tests for forgecore.embeddings.embedder.

These tests mock the SentenceTransformer model to avoid downloading the
real model (90+ MB) in CI. The shape and dtype contracts are what matter.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from forgecore.embeddings.embedder import Embedder


@pytest.fixture
def fake_model() -> MagicMock:
    """A mock SentenceTransformer that returns predictable embeddings."""
    mock = MagicMock()
    dim = 384  # match the configured embedding dimension

    def fake_encode(texts, **kwargs):
        # Deterministic: simple hash-based vector.
        arr = np.zeros((len(texts), dim), dtype=np.float32)
        for i, t in enumerate(texts):
            for j, ch in enumerate(t[:dim]):
                arr[i, j] = float(ord(ch) % 100) / 100.0
        return arr

    mock.encode.side_effect = fake_encode
    return mock


class TestEmbedder:
    def test_empty_input_returns_empty_array(self, fake_model: MagicMock) -> None:
        with patch("forgecore.embeddings.embedder.get_model", return_value=fake_model):
            embedder = Embedder()
            out = embedder.embed([])
        assert out.shape == (0, 384)
        assert out.dtype == np.float32

    def test_batch_returns_correct_shape(self, fake_model: MagicMock) -> None:
        with patch("forgecore.embeddings.embedder.get_model", return_value=fake_model):
            embedder = Embedder()
            out = embedder.embed(["hello", "world", "foo bar"])
        assert out.shape == (3, 384)
        assert out.dtype == np.float32

    def test_embed_query_returns_1d_vector(self, fake_model: MagicMock) -> None:
        with patch("forgecore.embeddings.embedder.get_model", return_value=fake_model):
            embedder = Embedder()
            out = embedder.embed_query("test query")
        assert out.ndim == 1
        assert out.shape == (384,)

    def test_dimension_property(self) -> None:
        embedder = Embedder()
        assert embedder.dimension == 384
