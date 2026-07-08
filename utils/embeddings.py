"""
embeddings.py

Responsible for:
- Loading the embedding model
- Generating vector embeddings for document chunks
"""

import config

from utils.embedding_model import get_embedding_model


def generate_embeddings(chunks):
    """
    Generate embeddings for all text chunks.

    Args:
        chunks (list):
            List of chunk dictionaries.

    Returns:
        list:
            Updated chunk list containing embeddings.
    """

    if not chunks:
        return []

    model = get_embedding_model()

    texts = [chunk["text"] for chunk in chunks]

    vectors = model.encode(
        texts,
        batch_size=getattr(config, "EMBEDDING_BATCH_SIZE", 32),
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True
    )

    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector

    return chunks
