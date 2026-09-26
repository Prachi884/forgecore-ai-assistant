"""Ingestion pipeline — orchestrates loading PDFs and chunking them.

This module ties together the loader and chunker and handles persistence to
JSONL. Stages 3+ will reuse the same Chunk format for embedding + indexing.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from forgecore.ingestion.chunker import chunk_documents
from forgecore.ingestion.models import Chunk, Document
from forgecore.ingestion.pdf_loader import load_pdf_directory
from forgecore.utils.config import get_settings
from forgecore.utils.paths import PROCESSED_DIR, RAW_DOCS_DIR, ensure_directory


@dataclass
class IngestionResult:
    """Summary of one ingestion run."""

    documents_loaded: int
    chunks_produced: int
    output_path: Path
    source_files: list[str]


def run_ingestion(
    raw_dir: Path | str | None = None,
    output_path: Path | str | None = None,
    pattern: str = "*.pdf",
) -> IngestionResult:
    """End-to-end ingestion: load → chunk → save JSONL.

    Parameters
    ----------
    raw_dir
        Directory containing source PDFs. Defaults to ``data/raw/``.
    output_path
        Where to write the JSONL chunks. Defaults to ``data/processed/chunks.jsonl``.
    pattern
        Glob to filter PDFs (default: all PDFs).

    Returns
    -------
    IngestionResult
        Summary of the run, suitable for logging or display in a UI.
    """
    logger = logging.getLogger(__name__)
    settings = get_settings()

    raw_dir_path = Path(raw_dir) if raw_dir else RAW_DOCS_DIR
    output_path_path = Path(output_path) if output_path else (PROCESSED_DIR / "chunks.jsonl")
    ensure_directory(output_path_path.parent)

    chunk_size = settings.app.chunking.chunk_size
    chunk_overlap = settings.app.chunking.chunk_overlap
    separators = list(settings.app.chunking.splitter_separators)

    logger.info("Starting ingestion from %s", raw_dir_path)
    logger.info(
        "Chunking config: chunk_size=%d, chunk_overlap=%d",
        chunk_size,
        chunk_overlap,
    )

    documents: list[Document] = load_pdf_directory(raw_dir_path, pattern=pattern)
    logger.info("Loaded %d documents", len(documents))

    if not documents:
        logger.warning("No documents found in %s — nothing to ingest.", raw_dir_path)
        return IngestionResult(
            documents_loaded=0,
            chunks_produced=0,
            output_path=output_path_path,
            source_files=[],
        )

    chunks: list[Chunk] = chunk_documents(
        documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    logger.info("Produced %d chunks", len(chunks))

    # Persist as JSONL: one chunk per line, easy to stream into Stage 3.
    source_files = sorted({d.source for d in documents})
    with output_path_path.open("w", encoding="utf-8") as fh:
        for chunk in chunks:
            fh.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")

    logger.info("Wrote %d chunks to %s", len(chunks), output_path_path)

    return IngestionResult(
        documents_loaded=len(documents),
        chunks_produced=len(chunks),
        output_path=output_path_path,
        source_files=source_files,
    )


def main() -> None:
    """CLI entry point: ``python -m forgecore.ingestion.pipeline``."""
    from forgecore.utils.logging import configure_logging

    configure_logging()
    result = run_ingestion()
    print(
        f"\nIngestion complete: {result.documents_loaded} documents -> "
        f"{result.chunks_produced} chunks -> {result.output_path}"
    )


if __name__ == "__main__":
    main()
