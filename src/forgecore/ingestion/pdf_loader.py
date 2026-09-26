"""PDF loader — extracts text from PDF files using PyMuPDF.

One PDF page → one Document. Each Document carries enough metadata (source file,
page number) to be cited back to the user when the RAG system answers a question.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf  # PyMuPDF

from forgecore.ingestion.models import Document


def load_pdf(pdf_path: Path | str) -> list[Document]:
    """Extract text from a PDF file, one Document per page.

    Empty pages (no extractable text — e.g. image-only scans) are skipped.

    Parameters
    ----------
    pdf_path
        Path to the PDF file.

    Returns
    -------
    list[Document]
        All non-empty pages, in original page order.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path}")

    source_name = path.name
    documents: list[Document] = []

    with pymupdf.open(path) as pdf:
        for page_idx, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if not text:
                # Skip image-only / empty pages.
                continue

            documents.append(
                Document(
                    doc_id=f"{source_name}::p{page_idx}",
                    text=text,
                    source=source_name,
                    page_number=page_idx,
                    metadata={
                        "title": pdf.metadata.get("title", ""),
                        "author": pdf.metadata.get("author", ""),
                        "total_pages": pdf.page_count,
                    },
                )
            )

    return documents


def load_pdf_directory(
    directory: Path | str,
    pattern: str = "*.pdf",
) -> list[Document]:
    """Load every PDF in `directory` matching `pattern`.

    Returns
    -------
    list[Document]
        All non-empty pages across all matching PDFs.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    all_documents: list[Document] = []
    pdf_files = sorted(dir_path.glob(pattern))

    if not pdf_files:
        return all_documents

    for pdf_path in pdf_files:
        all_documents.extend(load_pdf(pdf_path))

    return all_documents
