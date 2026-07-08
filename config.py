"""
config.py

Central configuration file for the ResearchMate AI application.
"""

# ==========================================================
# Text Chunking Configuration
# ==========================================================

# Maximum number of characters in each chunk.
# Larger chunks mean fewer embeddings, so document processing is faster.
CHUNK_SIZE = 1200

# Number of overlapping characters between consecutive chunks.
CHUNK_OVERLAP = 40

# ==========================================================
# Embedding Model Configuration
# ==========================================================

# Sentence Transformer model used for semantic embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Number of chunks encoded at once by Sentence Transformers
EMBEDDING_BATCH_SIZE = 64

# ==========================================================
# Retrieval Configuration
# ==========================================================

# Number of most relevant chunks retrieved from FAISS
TOP_K = 4

# Minimum cosine similarity score required for a chunk to be used.
# This helps reject unrelated questions before sending context to the LLM.
MIN_RELEVANCE_SCORE = 0.30

# Broad research tasks use the first representative chunks from each paper.
# Keeping this small makes Gemini respond faster.
BROAD_CONTEXT_MAX_CHUNKS = 8
BROAD_CONTEXT_CHUNKS_PER_DOCUMENT = 2

# Limit each chunk sent to Gemini to reduce prompt size and latency.
MAX_CONTEXT_CHARS_PER_CHUNK = 1000

# ==========================================================
# Gemini Model Configuration
# ==========================================================

# Gemini model used for answer generation
GEMINI_MODEL = "gemini-2.5-flash"

# Shorter generations are faster and usually enough for app responses.
GEMINI_MAX_OUTPUT_TOKENS = 600
GEMINI_TEMPERATURE = 0.2

# If Gemini does not respond quickly, the app falls back to a local
# document-based response instead of buffering indefinitely.
GEMINI_REQUEST_TIMEOUT_SECONDS = 8
