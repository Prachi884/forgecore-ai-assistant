"""ChromaDB-backed vector store with a clean Pythonic interface.

Responsibilities:
  - Persist vectors + text + metadata to disk.
  - Query by vector similarity.
  - Surface results in a friendly dataclass so callers don't depend on
    ChromaDB's raw output shape.

We use cosine distance because the embeddings are L2-normalised in the
Embedder, which makes cosine == dot product (cheaper to compute).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from forgecore.ingestion.models import Chunk
from forgecore.utils.config import get_settings
from forgecore.utils.paths import VECTOR_DB_DIR, ensure_directory

logger = logging.getLogger(__name__)


@dataclass
class RetrievalHit:
    """One result from a vector search."""

    chunk_id: str
    text: str
    source: str
    page_number: int
    chunk_index: int
    score: float  # higher is better; we convert distance → similarity
    metadata: dict = field(default_factory=dict)


class VectorStore:
    """Thin wrapper around a persistent ChromaDB collection.

    Examples
    --------
    >>> store = VectorStore()
    >>> store.count()
    0
    >>> store.add(chunks, embeddings)
    >>> hits = store.query(query_vector, top_k=5)
    """

    def __init__(self, persist_dir: Path | str | None = None) -> None:
        import chromadb  # heavy import, lazy

        persist_path = Path(persist_dir) if persist_dir else VECTOR_DB_DIR
        ensure_directory(persist_path)

        settings = get_settings()
        collection_name = settings.app.retrieval.collection_name

        self._client = chromadb.PersistentClient(path=str(persist_path))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # use cosine distance
        )
        logger.info(
            "VectorStore ready: collection=%s, items=%d",
            collection_name,
            self._collection.count(),
        )

    # ─── writes ────────────────────────────────────────────────────────
    def add(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        """Upsert chunks + their pre-computed embeddings.

        If a chunk_id already exists, ChromaDB updates it (no duplicates).
        """
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"chunks/embeddings length mismatch: {len(chunks)} vs {len(embeddings)}"
            )

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "source": c.source,
                "page_number": int(c.page_number),
                "chunk_index": int(c.chunk_index),
            }
            for c in chunks
        ]

        # ChromaDB wants plain Python lists for embeddings.
        emb_list = [emb.tolist() for emb in embeddings]
        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=emb_list,
            metadatas=metadatas,
        )
        logger.info("Upserted %d chunks", len(chunks))

    def clear(self) -> None:
        """Remove all items from the collection (preserves the collection itself)."""
        name = self._collection.name
        self._client.delete_collection(name)
        self._collection = self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Cleared collection %s", name)

    # ─── reads ─────────────────────────────────────────────────────────
    def count(self) -> int:
        return self._collection.count()

    def query(
        self,
        query_embedding: np.ndarray,
        top_k: int | None = None,
    ) -> list[RetrievalHit]:
        """Find the top-k chunks most similar to `query_embedding`.

        Distance is converted to similarity using ``score = 1 - distance``,
        which works for cosine distance with L2-normalised embeddings.
        """
        settings = get_settings()
        k = top_k or settings.app.retrieval.top_k

        if self._collection.count() == 0:
            logger.warning("Query against empty collection")
            return []

        result = self._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        hits: list[RetrievalHit] = []
        # ChromaDB returns parallel arrays. Take the first (and only) query.
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        for chunk_id, doc, meta, dist in zip(ids, documents, metadatas, distances, strict=True):
            meta = meta or {}
            hits.append(
                RetrievalHit(
                    chunk_id=chunk_id,
                    text=doc,
                    source=meta.get("source", "unknown"),
                    page_number=int(meta.get("page_number", 0)),
                    chunk_index=int(meta.get("chunk_index", 0)),
                    score=float(1.0 - dist),  # cosine distance → similarity
                    metadata=meta,
                )
            )
        return hits

    def get(self, chunk_ids: list[str]) -> list[Chunk]:
        """Fetch full Chunk objects by ID (useful for showing context)."""
        if not chunk_ids:
            return []
        result = self._collection.get(
            ids=chunk_ids,
            include=["documents", "metadatas"],
        )
        chunks: list[Chunk] = []
        for cid, doc, meta in zip(
            result["ids"], result["documents"], result["metadatas"], strict=True
        ):
            meta = meta or {}
            chunks.append(
                Chunk(
                    chunk_id=cid,
                    text=doc,
                    doc_id=cid.rsplit("::c", 1)[0],
                    source=meta.get("source", "unknown"),
                    page_number=int(meta.get("page_number", 0)),
                    chunk_index=int(meta.get("chunk_index", 0)),
                )
            )
        return chunks


def main() -> None:
    """CLI entry point (placeholder — use ``scripts/build_index.py`` instead)."""
    print("Use: python scripts/build_index.py")


if __name__ == "__main__":
    main()
