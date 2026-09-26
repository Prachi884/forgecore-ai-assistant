"""Embedding model wrapper around Sentence Transformers.

The model is loaded lazily on first use (not at import time) so unit tests
that mock the model don't have to download anything.
"""

from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np

from forgecore.utils.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_model():  # type: ignore[no-untyped-def]  # noqa: F821
    """Load (and cache) the embedding model. Downloads it on first call."""
    from sentence_transformers import SentenceTransformer  # heavy import, lazy

    settings = get_settings()
    model_name = settings.app.embeddings.model_name
    device = settings.app.embeddings.device
    logger.info("Loading embedding model %s on %s", model_name, device)
    return SentenceTransformer(model_name, device=device)


class Embedder:
    """Stateless wrapper for embedding text into vectors.

    Examples
    --------
    >>> embedder = Embedder()
    >>> vectors = embedder.embed(["hello world", "goodbye world"])
    >>> vectors.shape
    (2, 384)
    """

    def __init__(self) -> None:
        self._model = None

    @property
    def model(self):  # type: ignore[name-defined]  # noqa: F821
        if self._model is None:
            self._model = get_model()
        return self._model

    @property
    def dimension(self) -> int:
        return int(get_settings().app.embeddings.dimension)

    def embed(self, texts: list[str], show_progress: bool = False) -> np.ndarray:
        """Embed a batch of texts.

        Parameters
        ----------
        texts
            List of strings. Empty list returns an empty (0, dim) array.
        show_progress
            Whether to display a tqdm progress bar. Useful for big batches.

        Returns
        -------
        np.ndarray
            Shape ``(len(texts), dimension)``, dtype float32.
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        settings = get_settings()
        vectors = self.model.encode(
            texts,
            batch_size=settings.app.embeddings.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True,  # unit length → dot product == cosine similarity
        )
        return vectors.astype(np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a single query string. Returns a 1-D vector."""
        return self.embed([text], show_progress=False)[0]
