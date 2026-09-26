# ─── ForgeCore AI Assistant — Makefile ───────────────────────
# Convenient shortcuts. Run `make help` to see available targets.

# Use bash so we can use `source` if needed.
SHELL := /usr/bin/env bash

# Auto-detect Python — prefer the project-local .venv if it exists,
# otherwise fall back to whatever python3 is on PATH.
ifneq (,$(wildcard .venv/bin/python))
    PYTHON := .venv/bin/python
    PIP    := .venv/bin/python -m pip
else
    PYTHON ?= python3
    PIP    ?= $(PYTHON) -m pip
endif

VENV_ACTIVATE = . .venv/bin/activate 2>/dev/null || true

.DEFAULT_GOAL := help

.PHONY: help install install-dev install-ingestion install-retrieval install-llm install-ui install-all run test test-cov lint format clean clean-data clean-vectordb info

help: ## Show this help message
	@echo ""
	@echo "  ForgeCore AI Assistant — make targets"
	@echo "  ─────────────────────────────────────────────────"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

install: ## Install runtime dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install dev dependencies (includes runtime)
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

install-ingestion: ## Add PDF/document parsing libraries (Stage 2)
	$(PIP) install pymupdf reportlab

generate-docs: install-ingestion ## Generate the 10 fictional ForgeCore PDFs into data/raw/
	$(PYTHON) scripts/generate_documents.py

ingest: install-ingestion ## Run ingestion: load PDFs, chunk, write data/processed/chunks.jsonl
	$(PYTHON) scripts/ingest_documents.py

install-retrieval: ## Add embeddings + ChromaDB (Stage 3)
	$(PIP) install sentence-transformers chromadb

install-llm: ## Add Gemini client (Stage 5)
	$(PIP) install google-generativeai

install-ui: ## Add Streamlit (Stage 7)
	$(PIP) install streamlit

install-all: install-dev install-ingestion install-retrieval install-llm install-ui ## Install everything for all stages

run: ## Print the package version (Stage 1 smoke test)
	@$(PYTHON) -c "from forgecore import __version__, __stage__, __stage_name__; print(f'\n  ForgeCore AI Assistant') ; print(f'  Version : v{__version__}'); print(f'  Stage   : {__stage__} — {__stage_name__}\n')"

test: ## Run the test suite
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ --cov=forgecore --cov-report=term-missing

lint: ## Run ruff linter
	$(PYTHON) -m ruff check src tests

format: ## Auto-format with ruff
	$(PYTHON) -m ruff format src tests
	$(PYTHON) -m ruff check --fix src tests

clean: ## Remove caches and build artefacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	rm -rf build dist src/forgecore.egg-info
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

clean-data: ## Remove processed chunks (keeps raw PDFs)
	rm -rf data/processed/*

clean-vectordb: ## Wipe the ChromaDB store
	rm -rf chroma_db/*

info: ## Show environment info (Python version, key paths)
	@$(PYTHON) -c "from forgecore.utils.paths import PROJECT_ROOT, RAW_DOCS_DIR, VECTOR_DB_DIR; print(f'Project root : {PROJECT_ROOT}'); print(f'Raw docs dir : {RAW_DOCS_DIR}'); print(f'Vector DB    : {VECTOR_DB_DIR}')"
	@$(PYTHON) --version
