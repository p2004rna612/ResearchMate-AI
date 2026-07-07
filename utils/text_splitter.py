"""
text_splitter.py

Responsible for:
- Splitting extracted PDF pages into smaller chunks
- Preserving metadata required for retrieval and citations
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, CHUNK_OVERLAP


def get_text_splitter():
    """
    Create and return the RecursiveCharacterTextSplitter.
    """

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
    Split extracted PDF pages into text chunks.

    Args:
        pages (list):
            Output from load_pdf()

    Returns:
        list:
            List of chunk dictionaries.
    """

    splitter = get_text_splitter()

    chunks = []

    chunk_id = 1

    for page in pages:

        text_chunks = splitter.split_text(page["text"])

        for chunk in text_chunks:

            # Skip empty chunks
            if not chunk.strip():
                continue

            chunk_data = {
                "chunk_id": chunk_id,
                "document": page["document"],
                "page": page["page"],
                "source_id": page["source_id"],
                "text": chunk.strip()
            }

            if "source_label" in page:
                chunk_data["source_label"] = page["source_label"]

            if "source_url" in page:
                chunk_data["source_url"] = page["source_url"]

            chunks.append(chunk_data)

            chunk_id += 1

    return chunks
