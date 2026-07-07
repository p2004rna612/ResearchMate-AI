"""
document_loader.py

Loads supported document formats and normalizes them into the page structure
used by the RAG pipeline.
"""

from pathlib import Path

from utils.citation_utils import infer_research_link
from utils.pdf_loader import load_pdf


def _load_text_file(file_path, document_name=None):
    file_path = Path(file_path)
    name = document_name if document_name else file_path.name

    text = file_path.read_text(encoding="utf-8", errors="ignore").strip()

    if not text:
        return []

    research_link = infer_research_link(text, name)

    return [
        {
            "document": name,
            "page": 1,
            "text": text,
            "source_id": f"{Path(name).stem}_page_1",
            "source_label": research_link["label"],
            "source_url": research_link["url"],
        }
    ]


def _load_docx(file_path, document_name=None):
    try:
        from docx import Document
    except ImportError as exc:
        raise ImportError(
            "DOCX support requires python-docx. Run: pip install python-docx"
        ) from exc

    file_path = Path(file_path)
    name = document_name if document_name else file_path.name

    document = Document(file_path)
    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]
    text = "\n".join(paragraphs).strip()

    if not text:
        return []

    research_link = infer_research_link(text, name)

    return [
        {
            "document": name,
            "page": 1,
            "text": text,
            "source_id": f"{Path(name).stem}_page_1",
            "source_label": research_link["label"],
            "source_url": research_link["url"],
        }
    ]


def load_document(file_path, document_name=None):
    """
    Load a supported document type.

    Supported formats:
    - PDF
    - TXT
    - Markdown
    - DOCX
    """

    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path, document_name=document_name)

    if extension in {".txt", ".md", ".markdown"}:
        return _load_text_file(file_path, document_name=document_name)

    if extension == ".docx":
        return _load_docx(file_path, document_name=document_name)

    raise ValueError(f"Unsupported file type: {extension}")
