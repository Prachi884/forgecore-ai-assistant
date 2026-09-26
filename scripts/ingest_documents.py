"""CLI wrapper for running ingestion. Invoke via ``make ingest`` or directly."""

from __future__ import annotations

import sys

from forgecore.ingestion.pipeline import run_ingestion
from forgecore.utils.logging import configure_logging


def main() -> int:
    configure_logging()
    result = run_ingestion()
    print(
        f"\n  Ingestion summary\n"
        f"  ─────────────────────────────────\n"
        f"  Documents loaded : {result.documents_loaded}\n"
        f"  Chunks produced  : {result.chunks_produced}\n"
        f"  Output file      : {result.output_path}\n"
        f"  Source files     : {len(result.source_files)}\n"
    )
    for src in result.source_files:
        print(f"    • {src}")
    return 0 if result.documents_loaded > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
