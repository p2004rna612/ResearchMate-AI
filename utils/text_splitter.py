"""
text_splitter.py

Responsible for:
- Splitting extracted PDF text into chunks
- Preserving context using overlap
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_text_splitter():
    """
    Returns a configured text splitter.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    return splitter