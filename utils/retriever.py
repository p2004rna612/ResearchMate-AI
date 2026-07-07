"""
retriever.py

Responsible for:
- Converting user questions into embeddings
- Retrieving the most relevant document chunks
"""

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, MIN_RELEVANCE_SCORE, TOP_K

# ==========================================================
# Load Embedding Model (Loaded only once)
# ==========================================================

model = SentenceTransformer(EMBEDDING_MODEL)


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
