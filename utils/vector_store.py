"""
vector_store.py

Responsible for:
- Creating a FAISS vector index
- Storing document chunks
- Performing semantic similarity search
"""

import faiss
import numpy as np


class VectorStore:
    """
    FAISS vector database for semantic search.
    """

    def __init__(self, dimension):
        """
        Initialize FAISS index.

        Args:
            dimension (int): Embedding vector dimension.
        """

        # Since embeddings are normalized,
        # Inner Product acts like Cosine Similarity.
        self.index = faiss.IndexFlatIP(dimension)

        self.chunks = []

    def add_chunks(self, chunks):
        """
        Add embedded chunks to FAISS.

        Args:
            chunks (list): List of chunk dictionaries.
        """

        if not chunks:
            return

        vectors = np.array(
            [chunk["embedding"] for chunk in chunks],
            dtype="float32"
        )

        self.index.add(vectors)

        self.chunks.extend(chunks)

    def search(self, query_embedding, top_k=5):
        """
        Search for the most relevant chunks.

        Args:
            query_embedding (numpy.ndarray)
            top_k (int)

        Returns:
            list
        """

        query = np.array(
            [query_embedding],
            dtype="float32"
        )

        scores, indices = self.index.search(
            query,
            top_k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx != -1:
                chunk = dict(self.chunks[idx])
                chunk["score"] = float(score)
                results.append(chunk)

        return results
