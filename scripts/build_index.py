"""Build (or rebuild) the ChromaDB index from chunks.jsonl.

Pipeline:
  1. Load chunks from data/processed/chunks.jsonl
  2. Embed each chunk's text with sentence-transformers
  3. Upsert into ChromaDB at chroma_db/

Run with:  python scripts/build_index.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from forgecore.embeddings.embedder import Embedder
from forgecore.ingestion.models import Chunk
from forgecore.retrieval.vector_store import VectorStore
from forgecore.utils.logging import configure_logging
from forgecore.utils.paths import PROCESSED_DIR


def _load_chunks(jsonl_path: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    if not jsonl_path.is_file():
        return chunks
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            chunks.append(Chunk(**data))
    return chunks


def main() -> int:
    configure_logging()
    chunks_path = PROCESSED_DIR / "chunks.jsonl"
    chunks = _load_chunks(chunks_path)

    if not chunks:
        print(f"  ! No chunks found at {chunks_path}")
        print("    Run `make ingest` first to generate chunks.")
        return 1

    print(f"  + Loaded {len(chunks)} chunks from {chunks_path}")

    # Embed
    embedder = Embedder()
    print(f"  + Embedding model loaded (dim={embedder.dimension})")
    print(f"  + Generating embeddings (dim={embedder.dimension})...")
    embeddings = embedder.embed([c.text for c in chunks], show_progress=True)

    print(f"  + Generated {embeddings.shape[0]} vectors of shape ({embeddings.shape[0]}, {embeddings.shape[1]})")

    # Store
    store = VectorStore()
    store.clear()  # start fresh — easier to reason about than diff
    store.add(chunks, embeddings)

    print()
    print(f"  Index built successfully")
    print(f"  ─────────────────────────────────")
    print(f"  Collection    : {store._collection.name}")
    print(f"  Items indexed : {store.count()}")
    print(f"  Embedding dim : {embedder.dimension}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
