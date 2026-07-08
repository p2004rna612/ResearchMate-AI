"""
retriever.py

Responsible for:
- Converting user questions into embeddings
- Retrieving the most relevant document chunks
"""

from config import MIN_RELEVANCE_SCORE, TOP_K
from utils.embedding_model import get_embedding_model


def retrieve(query, vector_store):
    """
    Retrieve the most relevant chunks for a user query.

    Args:
        query (str):
            User's question.

        vector_store (VectorStore):
            FAISS vector database.

    Returns:
        list:
            Top-K most relevant chunks.
    """

    if not query.strip():
        return []

    model = get_embedding_model()

    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    results = vector_store.search(
        query_embedding,
        top_k=TOP_K
    )

    return [
        chunk
        for chunk in results
        if chunk.get("score", 0) >= MIN_RELEVANCE_SCORE
    ]
