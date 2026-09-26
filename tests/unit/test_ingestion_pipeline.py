"""Integration test for the ingestion pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pymupdf
import pytest

from forgecore.ingestion.pipeline import run_ingestion


@pytest.fixture
def fake_pdf_dir(tmp_path: Path) -> Path:
    """Create a directory with two minimal one-page PDFs."""
    pdf_dir = tmp_path / "raw"
    pdf_dir.mkdir()
    for name, content in [("alpha.pdf", "Alpha product information. " * 30), ("beta.pdf", "Beta specifications and pricing. " * 30)]:
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((50, 72), content)
        doc.save(pdf_dir / name)
        doc.close()
    return pdf_dir


class TestRunIngestion:
    def test_end_to_end_produces_jsonl(self, fake_pdf_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "chunks.jsonl"
        result = run_ingestion(raw_dir=fake_pdf_dir, output_path=output)

        assert result.documents_loaded == 2
        assert result.chunks_produced >= 2
        assert output.exists()

        with output.open() as fh:
            lines = [json.loads(line) for line in fh if line.strip()]
        assert len(lines) == result.chunks_produced
        for entry in lines:
            assert "chunk_id" in entry
            assert "text" in entry
            assert "source" in entry
            assert "page_number" in entry

    def test_empty_directory_returns_zero(self, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        output = tmp_path / "out.jsonl"
        result = run_ingestion(raw_dir=empty_dir, output_path=output)
        assert result.documents_loaded == 0
        assert result.chunks_produced == 0
