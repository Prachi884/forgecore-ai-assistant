"""Tests for forgecore.ingestion.pdf_loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from forgecore.ingestion.pdf_loader import load_pdf, load_pdf_directory


class TestLoadPdf:
    def test_returns_documents_for_each_page(self, tmp_path: Path) -> None:
        # Use one of our generated fixtures.
        fixture = Path(__file__).parents[1] / "fixtures" / "sample.pdf"
        if not fixture.exists():
            pytest.skip("sample.pdf fixture not present")

        docs = load_pdf(fixture)
        assert len(docs) >= 1
        for d in docs:
            assert d.text.strip()
            assert d.source.endswith(".pdf")
            assert d.page_number >= 1

    def test_raises_for_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_pdf(tmp_path / "nope.pdf")

    def test_raises_for_non_pdf_extension(self, tmp_path: Path) -> None:
        fake = tmp_path / "data.txt"
        fake.write_text("not a pdf")
        with pytest.raises(ValueError):
            load_pdf(fake)


class TestLoadPdfDirectory:
    def test_returns_empty_for_empty_directory(self, tmp_path: Path) -> None:
        docs = load_pdf_directory(tmp_path)
        assert docs == []

    def test_raises_for_non_directory(self, tmp_path: Path) -> None:
        fake = tmp_path / "afile.txt"
        fake.write_text("x")
        with pytest.raises(NotADirectoryError):
            load_pdf_directory(fake)

    def test_loads_multiple_pdfs(self, tmp_path: Path) -> None:
        # Generate two minimal one-page PDFs at runtime.
        import pymupdf

        for i in range(2):
            doc = pymupdf.open()
            page = doc.new_page()
            page.insert_text((50, 72), f"Hello from page {i}")
            doc.save(tmp_path / f"test_{i}.pdf")
            doc.close()

        docs = load_pdf_directory(tmp_path)
        assert len(docs) == 2
        assert {d.source for d in docs} == {"test_0.pdf", "test_1.pdf"}
        assert all(d.page_number == 1 for d in docs)
        assert "Hello from page" in docs[0].text + docs[1].text
