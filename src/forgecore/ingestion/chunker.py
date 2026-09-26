"""Recursive character-based text chunker.

Splits documents into overlapping chunks using a hierarchy of separators
(paragraph → sentence → word → character). We don't pull in langchain or
similar — the algorithm is small enough to own.

The chunker is deliberately simple and tunable: chunk_size and chunk_overlap
come from settings.yaml so you can experiment without editing code.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from forgecore.ingestion.models import Chunk, Document


def _split_by_separator(text: str, separator: str) -> list[str]:
    """Split `text` by `separator`, dropping empty results."""
    if separator == "":
        return list(text)
    parts = text.split(separator)
    return [p for p in parts if p]


def _merge_pieces(pieces: list[str], chunk_size: int, separator: str) -> list[str]:
    """Merge small pieces into chunks no larger than `chunk_size`.

    Joins pieces with `separator`. Pieces that are themselves longer than
    `chunk_size` are passed through (they'll be split recursively upstream).
    """
    chunks: list[str] = []
    current = ""

    for piece in pieces:
        candidate = current + separator + piece if current else piece
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # If this single piece is bigger than chunk_size, it has to go alone
            # — we'll handle it in a higher recursion level.
            current = piece

    if current:
        chunks.append(current)

    return chunks


def _recursive_split(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    """Recursively split `text` until every chunk fits in `chunk_size` chars."""
    if len(text) <= chunk_size:
        return [text]

    if not separators:
        # No separators left — hard character split.
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    separator = separators[0]
    remaining_separators = separators[1:]
    pieces = _split_by_separator(text, separator)

    # Reconstruct chunks, then split anything still too big recursively.
    merged = _merge_pieces(pieces, chunk_size, separator)
    final: list[str] = []
    for chunk in merged:
        if len(chunk) <= chunk_size:
            final.append(chunk)
        else:
            final.extend(_recursive_split(chunk, chunk_size, remaining_separators))
    return final


def _add_overlap(chunks: list[str], overlap: int) -> list[str]:
    """Prepend the tail of the previous chunk to each subsequent chunk.

    This gives the retriever some context around chunk boundaries. The first
    chunk is kept as-is.
    """
    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    out: list[str] = [chunks[0]]
    for chunk in chunks[1:]:
        tail = chunks[len(out) - 1][-overlap:]
        # Avoid duplicating identical leading text if previous chunk ends with
        # the same characters.
        if chunk.startswith(tail):
            out.append(chunk)
        else:
            out.append(tail + chunk)
    return out


def _normalise(text: str) -> str:
    """Collapse runs of whitespace inside a chunk so embeddings aren't noisy."""
    # Collapse 3+ newlines into 2; collapse other whitespace to single space.
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_document(
    document: Document,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separators: list[str] | None = None,
) -> list[Chunk]:
    """Split a single Document into Chunks.

    Parameters
    ----------
    document
        The document to chunk.
    chunk_size
        Target maximum characters per chunk.
    chunk_overlap
        Characters of overlap between consecutive chunks.
    separators
        Ordered list of separators to try when splitting. ``None`` uses a default
        priority list (paragraph → sentence → word).
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    raw_chunks = _recursive_split(document.text, chunk_size, separators)
    raw_chunks = [_normalise(c) for c in raw_chunks]
    raw_chunks = [c for c in raw_chunks if c]  # drop empties
    raw_chunks = _add_overlap(raw_chunks, chunk_overlap)

    return [
        Chunk(
            chunk_id=f"{document.doc_id}::c{idx}",
            text=text,
            doc_id=document.doc_id,
            source=document.source,
            page_number=document.page_number,
            chunk_index=idx,
            metadata=dict(document.metadata),
        )
        for idx, text in enumerate(raw_chunks)
    ]


def chunk_documents(
    documents: Iterable[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separators: list[str] | None = None,
) -> list[Chunk]:
    """Chunk every Document in an iterable."""
    all_chunks: list[Chunk] = []
    for doc in documents:
        all_chunks.extend(
            chunk_document(
                doc,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=separators,
            )
        )
    return all_chunks
