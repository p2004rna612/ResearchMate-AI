"""
embedding_model.py

Shared lazy loader for the Sentence Transformer embedding model.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the embedding model only when it is first needed.

    local_files_only avoids repeated Hugging Face metadata requests during
    Streamlit reruns, which can fail if the shared HTTP client was closed.
    """

    try:
        return SentenceTransformer(
            EMBEDDING_MODEL,
            local_files_only=True,
        )
    except TypeError:
        return SentenceTransformer(EMBEDDING_MODEL)
