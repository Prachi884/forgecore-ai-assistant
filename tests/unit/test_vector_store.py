"""Tests for forgecore.retrieval.vector_store (using a temp ChromaDB)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from forgecore.ingestion.models import Chunk
from forgecore.retrieval.vector_store import RetrievalHit, VectorStore


def _make_chunk(idx: int, source: str = "test.pdf", page: int = 1, text: str = "") -> Chunk:
    return Chunk(
        chunk_id=f"{source}::p{page}::c{idx}",
        text=text or f"sample chunk text {idx}",
        doc_id=f"{source}::p{page}",
        source=source,
        page_number=page,
        chunk_index=idx,
    )


def _make_unit_vector(seed: int, dim: int = 384) -> np.ndarray:
    """Deterministic unit vector for tests."""
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / np.linalg.norm(v)


class TestVectorStore:
    def test_starts_empty(self, tmp_path: Path) -> None:
        store = VectorStore(persist_dir=tmp_path)
        assert store.count() == 0

    def test_add_and_count(self, tmp_path: Path) -> None:
        store = VectorStore(persist_dir=tmp_path)
        chunks = [_make_chunk(i) for i in range(3)]
        embeddings = np.stack([_make_unit_vector(i) for i in range(3)])
        store.add(chunks, embeddings)
        assert store.count() == 3

    def test_upsert_is_idempotent(self, tmp_path: Path) -> None:
        store = VectorStore(persist_dir=tmp_path)
        chunks = [_make_chunk(0, text="original")]
        embeddings = np.stack([_make_unit_vector(0)])
        store.add(chunks, embeddings)
        # Re-add same ID with different text
        chunks2 = [_make_chunk(0, text="updated")]
        embeddings2 = np.stack([_make_unit_vector(0)])
        store.add(chunks2, embeddings2)
        assert store.count() == 1
        hits = store.query(_make_unit_vector(0), top_k=1)
        assert hits[0].text == "updated"

    def test_query_returns_top_k(self, tmp_path: Path) -> None:
        store = VectorStore(persist_dir=tmp_path)
        chunks = [_make_chunk(i, text=f"text {i}") for i in range(10)]
        embeddings = np.stack([_make_unit_vector(i) for i in range(10)])
        store.add(chunks, embeddings)

        # Query with vector #3's embedding; should return #3 first.
        hits = store.query(_make_unit_vector(3), top_k=3)
        assert len(hits) == 3
        assert all(isinstance(h, RetrievalHit) for h in hits)
        # Top hit should be chunk #3 (identical embedding)
        assert hits[0].chunk_index == 3
        assert hits[0].score > 0.99  # near-perfect similarity

    def test_query_against_empty_store(self, tmp_path: Path) -> None:
        store = VectorStore(persist_dir=tmp_path)
        hits = store.query(_make_unit_vector(0), top_k=5)
        assert hits == []

    def test_clear_empties_collection(self, tmp_path: Path) -> None:
        store = VectorStore(persist_dir=tmp_path)
        chunks = [_make_chunk(0)]
        embeddings = np.stack([_make_unit_vector(0)])
        store.add(chunks, embeddings)
        assert store.count() == 1
        store.clear()
        assert store.count() == 0

    def test_metadata_round_trip(self, tmp_path: Path) -> None:
        store = VectorStore(persist_dir=tmp_path)
        chunks = [_make_chunk(0, source="important.pdf", page=7)]
        embeddings = np.stack([_make_unit_vector(0)])
        store.add(chunks, embeddings)
        hits = store.query(_make_unit_vector(0), top_k=1)
        assert hits[0].source == "important.pdf"
        assert hits[0].page_number == 7

    def test_length_mismatch_raises(self, tmp_path: Path) -> None:
        store = VectorStore(persist_dir=tmp_path)
        chunks = [_make_chunk(0), _make_chunk(1)]
        embeddings = np.stack([_make_unit_vector(0)])  # only one
        with pytest.raises(ValueError):
            store.add(chunks, embeddings)
