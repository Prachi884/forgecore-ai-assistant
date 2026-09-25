# ForgeCore AI Knowledge Assistant

> A Retrieval-Augmented Generation (RAG) system that lets employees ask natural-language questions about ForgeCore Industries' internal documents — product specs, SOPs, quality docs, policies — and get grounded, citation-backed answers.

This is a **portfolio project** built progressively in stages, using only **free / open-source tools**. The fictional company **ForgeCore Industries** is a B2B manufacturer of industrial crucibles and foundry consumables.

---

## ✨ What this project demonstrates

| Skill | Where it shows up |
|---|---|
| Python packaging | `pyproject.toml`, layered `src/forgecore/` layout |
| Configuration management | YAML + `.env` via `pydantic-settings` |
| Vector search | ChromaDB + Sentence Transformers |
| LLM integration | Google Gemini API (free tier) |
| Web UI | Streamlit |
| Production engineering | Logging, tests, lint, CI, evaluation harness |
| Version control | Git + GitHub |

---

## 🏗️ Architecture

```
                  ┌──────────────────┐
                  │ Company PDFs     │  ← data/raw/
                  └────────┬─────────┘
                           ↓
                    ┌──────────────┐
                    │   PyMuPDF    │  ← src/forgecore/ingestion/pdf_loader.py
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Chunking   │  ← src/forgecore/ingestion/chunker.py
                    └──────┬───────┘
                           ↓
                ┌─────────────────────┐
                │ Sentence Transformer│  ← src/forgecore/embeddings/embedder.py
                └──────────┬──────────┘
                           ↓
                    ┌─────────────┐
                    │  ChromaDB   │  ← src/forgecore/retrieval/vector_store.py
                    └──────┬──────┘
                           │
                    User Question
                           ↓
                    Query Embedding
                           ↓
                    Similarity Search (top-k)
                           ↓
                   Relevant Document Chunks
                           ↓
                    ┌─────────────┐
                    │ Gemini API  │  ← src/forgecore/generation/llm_client.py
                    └──────┬──────┘
                           ↓
              Grounded Answer + Source Citations
                           ↓
                       Streamlit  ← app/streamlit_app.py
```

---

## 🛠️ Tech stack (all free)

| Component | Tool |
|---|---|
| Dev environment | GitHub Codespaces (60 hrs/month free) |
| Language | Python 3.11+ |
| PDF extraction | PyMuPDF |
| PDF generation (fictional docs) | ReportLab |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector database | ChromaDB |
| LLM | Google Gemini API (`gemini-2.0-flash`, free tier) |
| UI | Streamlit |
| Tests | pytest + pytest-cov |
| Lint/format | Ruff |
| CI | GitHub Actions |

---

## 🚀 Getting started

### Option A — GitHub Codespaces (recommended, no local install)

1. Push this repo to GitHub.
2. Click **Code → Codespaces → Create codespace on `main`**.
3. Wait ~90 seconds for the dev container to build.
4. The terminal opens automatically. Run:
   ```bash
   make run      # smoke test — prints version + stage
   make test     # runs the test suite
   ```

### Option B — Local machine

```bash
git clone <repo-url> forgecore-ai-assistant
cd forgecore-ai-assistant
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
make install-dev
make run
```

---

## 📁 Project layout

```
forgecore-ai-assistant/
├── config/
│   └── settings.yaml              # All tunables (chunk size, models, top-k)
├── data/
│   ├── raw/                       # Original PDFs (gitignored)
│   ├── processed/                 # Extracted chunks (regenerated)
│   └── eval/                      # Golden Q&A pairs for evaluation
├── chroma_db/                     # Persisted vector store (gitignored)
├── src/forgecore/
│   ├── ingestion/                 # Stage 2 — PDF loader, chunker
│   ├── embeddings/                # Stage 3 — embedding model wrapper
│   ├── retrieval/                 # Stage 3-4 — ChromaDB + retriever
│   ├── generation/                # Stage 5-6 — Gemini client, answerer
│   ├── rag/                       # Stage 5 — end-to-end pipeline
│   ├── evaluation/                # Stage 8 — quality metrics
│   └── utils/                     # paths, logging, config
├── scripts/                       # CLI entry points
├── app/                           # Streamlit UI
├── tests/                         # pytest suite
├── notebooks/                     # Exploration (kept separate from prod)
├── docs/                          # Architecture, data model, eval reports
├── .devcontainer/                 # Codespaces config
├── .github/workflows/             # CI
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── .env.example
└── README.md
```

---

## 🔐 Environment variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

| Variable | Purpose | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (free tier) | <https://aistudio.google.com/apikey> |

No credit card needed. The free tier gives ~1,500 requests/day — more than enough for this project.

---

## 🧭 Build stages

We build this project in small, verifiable stages. Each stage produces something you can run.

| Stage | Status | What it adds |
|---|---|---|
| 1. Foundation | ✅ | Repo scaffold, Codespaces, config, logging, paths, tests, CI |
| 2. Document ingestion | ⏳ | PDF loader + chunker, generate ForgeCore's fictional docs |
| 3. Embeddings + vector store | ⏳ | Sentence Transformers + ChromaDB |
| 4. Retrieval CLI | ⏳ | Query the index from the command line |
| 5. LLM integration | ⏳ | Gemini API client, prompt templates |
| 6. Citations | ⏳ | Source pages attached to every answer |
| 7. Streamlit UI | ⏳ | Browser-based chat interface |
| 8. Evaluation harness | ⏳ | Golden Q&A set + hit-rate/MRR metrics |
| 9. FastAPI (later) | ⏳ | REST endpoint |
| 10. SQL bridge (later) | ⏳ | Hybrid structured + unstructured queries |

---

## 📜 License

MIT — see `LICENSE`.

---

## 🙋 About

Built as a portfolio piece to demonstrate end-to-end RAG engineering: data ingestion → embeddings → vector search → LLM orchestration → UI → evaluation → CI. Everything here uses free tools and runs on GitHub Codespaces.
