"""Integration test for the build-index pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from forgecore.ingestion.models import Chunk


def _write_chunks_jsonl(path: Path, chunks: list[Chunk]) -> None:
    with path.open("w") as fh:
        for c in chunks:
            fh.write(json.dumps(c.to_dict()) + "\n")


def _fake_embedder(texts: list[str], dim: int = 384, **_kwargs) -> np.ndarray:
    rng = np.random.default_rng(seed=42)
    arr = rng.standard_normal((len(texts), dim)).astype(np.float32)
    # Normalise so cosine works
    arr = arr / np.linalg.norm(arr, axis=1, keepdims=True)
    return arr


class TestBuildIndex:
    def test_end_to_end_with_mocked_embedder(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Create fake chunks.jsonl
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        chunks = [
            Chunk(
                chunk_id=f"doc.pdf::p1::c{i}",
                text=f"sample text {i}",
                doc_id="doc.pdf::p1",
                source="doc.pdf",
                page_number=1,
                chunk_index=i,
            )
            for i in range(5)
        ]
        _write_chunks_jsonl(processed_dir / "chunks.jsonl", chunks)

        # Monkey-patch settings paths via env-vars? Easier: directly use a store in tmp_path.
        # We'll patch the VectorStore to use tmp_path
        chroma_dir = tmp_path / "chroma"

        # Mock the Embedder to avoid downloading the real model
        mock_embedder = MagicMock()
        mock_embedder.embed.side_effect = _fake_embedder
        mock_embedder.dimension = 384

        with (
            patch("forgecore.embeddings.embedder.Embedder", return_value=mock_embedder),
            patch("forgecore.retrieval.vector_store.VECTOR_DB_DIR", chroma_dir),
        ):
            # Simulate the build_index flow
            from scripts.build_index import _load_chunks

            from forgecore.embeddings.embedder import Embedder
            from forgecore.retrieval.vector_store import VectorStore

            loaded = _load_chunks(processed_dir / "chunks.jsonl")
            assert len(loaded) == 5

            embedder = Embedder()
            embeddings = embedder.embed([c.text for c in loaded])
            assert embeddings.shape == (5, 384)

            store = VectorStore(persist_dir=chroma_dir)
            store.clear()
            store.add(loaded, embeddings)

            assert store.count() == 5

            # Query and verify
            hits = store.query(embeddings[0], top_k=3)
            assert len(hits) == 3
            assert hits[0].chunk_index == 0  # exact match scores highest
