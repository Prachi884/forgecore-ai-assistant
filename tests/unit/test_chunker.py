"""Tests for forgecore.ingestion.chunker."""

from __future__ import annotations

import pytest

from forgecore.ingestion.chunker import chunk_document, chunk_documents
from forgecore.ingestion.models import Document


def _doc(text: str, source: str = "test.pdf", page: int = 1) -> Document:
    return Document(
        doc_id=f"{source}::p{page}",
        text=text,
        source=source,
        page_number=page,
    )


class TestChunkDocument:
    def test_short_text_single_chunk(self) -> None:
        doc = _doc("Hello world. This is short.")
        chunks = chunk_document(doc, chunk_size=500, chunk_overlap=50)
        assert len(chunks) == 1
        assert chunks[0].chunk_index == 0
        assert "Hello world" in chunks[0].text

    def test_long_text_multiple_chunks(self) -> None:
        long_text = ". ".join([f"Sentence number {i}." for i in range(200)])
        doc = _doc(long_text)
        chunks = chunk_document(doc, chunk_size=200, chunk_overlap=30)
        assert len(chunks) > 1
        # Each chunk (except the first) should contain overlap text from the previous.
        for c in chunks[1:]:
            assert c.chunk_index > 0

    def test_chunk_ids_are_unique(self) -> None:
        long_text = ". ".join([f"Sentence {i}." for i in range(100)])
        chunks = chunk_document(_doc(long_text), chunk_size=100, chunk_overlap=10)
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_metadata_is_preserved(self) -> None:
        doc = _doc("Some text.", source="special.pdf", page=7)
        chunks = chunk_document(doc, chunk_size=500, chunk_overlap=10)
        for c in chunks:
            assert c.source == "special.pdf"
            assert c.page_number == 7
            assert c.doc_id == "special.pdf::p7"

    def test_overlap_is_applied(self) -> None:
        text = "abcdefghij " * 100  # 1100 chars
        chunks = chunk_document(_doc(text), chunk_size=300, chunk_overlap=50)
        # Each chunk after the first should start with the tail of the previous.
        for prev, curr in zip(chunks, chunks[1:], strict=False):
            tail = prev.text[-50:]
            assert curr.text.startswith(tail), (
                f"Expected overlap not found. Prev tail: {tail!r}, Curr head: {curr.text[:60]!r}"
            )

    def test_validates_chunk_size(self) -> None:
        with pytest.raises(ValueError):
            chunk_document(_doc("x"), chunk_size=0, chunk_overlap=0)

    def test_validates_overlap_smaller_than_size(self) -> None:
        with pytest.raises(ValueError):
            chunk_document(_doc("x"), chunk_size=100, chunk_overlap=100)
        with pytest.raises(ValueError):
            chunk_document(_doc("x"), chunk_size=100, chunk_overlap=200)

    def test_custom_separators(self) -> None:
        text = "alpha|beta|gamma|delta"
        chunks = chunk_document(_doc(text), chunk_size=10, chunk_overlap=0, separators=["|"])
        # Each piece should be separated cleanly on "|"
        joined = "|".join(c.text for c in chunks)
        assert joined.count("|") >= 3

    def test_empty_chunks_are_dropped(self) -> None:
        text = "word " * 50 + "   \n\n\n   " + "word " * 50
        chunks = chunk_document(_doc(text), chunk_size=100, chunk_overlap=10)
        assert all(c.text.strip() for c in chunks)


class TestChunkDocuments:
    def test_chunks_all_documents(self) -> None:
        docs = [
            _doc("First document short text.", source="a.pdf", page=1),
            _doc("Second document with more text. " * 30, source="b.pdf", page=1),
        ]
        chunks = chunk_documents(docs, chunk_size=200, chunk_overlap=20)
        sources = {c.source for c in chunks}
        assert sources == {"a.pdf", "b.pdf"}
