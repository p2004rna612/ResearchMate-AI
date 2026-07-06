"""
text_splitter.py

Responsible for:
- Splitting extracted PDF pages into chunks
- Preserving metadata for citations
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP


def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )


def split_pages(pages):
    """
    Split extracted PDF pages into chunks.

    Args:
        pages: List of dictionaries returned by pdf_loader

    Returns:
        List of chunk dictionaries.
    """

    splitter = get_text_splitter()

    chunks = []

    chunk_id = 1

    for page in pages:

        text_chunks = splitter.split_text(page["text"])

        for chunk in text_chunks:

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document": page["document"],
                    "page": page["page"],
                    "source_id": page["source_id"],
                    "text": chunk
                }
            )

            chunk_id += 1

    return chunks