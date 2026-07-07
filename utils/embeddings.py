"""
embeddings.py

Responsible for:
- Loading the embedding model
- Generating vector embeddings for document chunks
"""

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL

# ==========================================================
# Load Embedding Model (Loaded only once)
# ==========================================================

model = SentenceTransformer(EMBEDDING_MODEL)


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

    texts = [chunk["text"] for chunk in chunks]

    vectors = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector

    return chunks