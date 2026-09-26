"""Data models used by the ingestion pipeline.

Two main types:

- `Document` — a single page of a PDF (or other source), with metadata.
- `Chunk` — a slice of a Document's text, ready for embedding.

Keeping these as frozen dataclasses makes them easy to serialise to JSONL and
trivial to reason about in tests.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Document:
    """A single page extracted from a source document.

    Attributes
    ----------
    doc_id
        Stable identifier — ``"{source}::p{page_number}"``.
    text
        The full text of the page.
    source
        File name (without path) of the originating document.
    page_number
        1-indexed page number within the source.
    metadata
        Free-form extra info (e.g. title, author, year).
    """

    doc_id: str
    text: str
    source: str
    page_number: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Chunk:
    """A text chunk produced by splitting a Document.

    Attributes
    ----------
    chunk_id
        Stable identifier — ``"{doc_id}::c{chunk_index}"``.
    text
        The chunk's text content (used for embedding).
    doc_id
        Reference back to the parent Document.
    source
        File name of the parent document (denormalised for convenience).
    page_number
        Page number of the parent document.
    chunk_index
        0-indexed position of this chunk within the parent document.
    metadata
        Inherited + chunk-specific metadata.
    """

    chunk_id: str
    text: str
    doc_id: str
    source: str
    page_number: int
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
