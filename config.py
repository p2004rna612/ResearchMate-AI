"""
config.py

Central configuration file for the ResearchMate AI application.
"""

# ==========================================================
# Text Chunking Configuration
# ==========================================================

# Maximum number of characters in each chunk
CHUNK_SIZE = 500

# Number of overlapping characters between consecutive chunks
CHUNK_OVERLAP = 100

# ==========================================================
# Embedding Model Configuration
# ==========================================================

# Sentence Transformer model used for semantic embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ==========================================================
# Retrieval Configuration
# ==========================================================

# Number of most relevant chunks retrieved from FAISS
TOP_K = 5

# ==========================================================
# Gemini Model Configuration
# ==========================================================

# Gemini model used for answer generation
GEMINI_MODEL = "gemini-2.5-flash"