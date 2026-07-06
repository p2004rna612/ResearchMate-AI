"""
embeddings.py

Responsible for:
- Loading the embedding model
- Converting text into vector embeddings
"""

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

# Load the model only once
model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embeddings(chunks):
    """
    Generate embeddings for all text chunks.

    Args:
        chunks: List of chunk dictionaries

    Returns:
        Updated chunk list with embeddings
    """

    texts = [chunk["text"] for chunk in chunks]

    vectors = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector

    return chunks