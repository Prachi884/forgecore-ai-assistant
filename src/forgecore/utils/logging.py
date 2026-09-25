"""Structured logging setup for the ForgeCore project.

We use Rich for prettier console output in development. Falls back to plain
stdlib logging if Rich isn't installed (e.g. in a slim CI image).
"""

from __future__ import annotations

import logging
import sys

from forgecore.utils.paths import LOGS_DIR, ensure_directory

try:
    from rich.logging import RichHandler

    _RICH_AVAILABLE = True
except ImportError:  # pragma: no cover
    _RICH_AVAILABLE = False


_DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DEFAULT_LEVEL = "INFO"


def configure_logging(level: str = _DEFAULT_LEVEL) -> None:
    """Configure root logger. Call once at application startup.

    Parameters
    ----------
    level
        Logging level name — DEBUG, INFO, WARNING, ERROR. Case-insensitive.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    ensure_directory(LOGS_DIR)

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Remove any pre-existing handlers (Streamlit re-imports modules).
    for handler in list(root.handlers):
        root.removeHandler(handler)

    if _RICH_AVAILABLE:
        handler: logging.Handler = RichHandler(
            level=numeric_level,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=False,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
    else:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))

    root.addHandler(handler)

    # Quiet down noisy third-party loggers.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for `name` (typically __name__)."""
    return logging.getLogger(name)
