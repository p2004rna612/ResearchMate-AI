"""
pdf_loader.py

Responsible for:
- Reading PDF files
- Extracting text page by page
- Preserving document metadata
"""

from pathlib import Path
import pdfplumber
import pypdfium2 as pdfium

from utils.citation_utils import infer_research_link


def _extract_pages_with_pdfium(pdf_path, name):
    pages = []

    pdf = pdfium.PdfDocument(pdf_path)

    try:
        for page_index, page in enumerate(pdf, start=1):
            text_page = page.get_textpage()
            text = text_page.get_text_range()

            if not text or not text.strip():
                continue

            pages.append(
                {
                    "document": name,
                    "page": page_index,
                    "text": text.strip(),
                    "source_id": f"{Path(name).stem}_page_{page_index}",
                }
            )
    finally:
        pdf.close()

    return pages


def _extract_pages_with_pdfplumber(pdf_path, name):
    pages = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()

            if not text or not text.strip():
                continue

            pages.append(
                {
                    "document": name,
                    "page": page_number,
                    "text": text.strip(),
                    "source_id": f"{Path(name).stem}_page_{page_number}",
                }
            )

    return pages


def load_pdf(pdf_path, document_name=None):
    """
    Load a PDF and extract text from each page.

    Args:
        pdf_path (str | Path):
            Path to the PDF.

        document_name (str, optional):
            Original filename. Used when uploaded through Streamlit.

    Returns:
        list[dict]

        Example:

        [
            {
                "document": "bert.pdf",
                "page": 1,
                "text": "...",
                "source_id": "bert_page_1"
            }
        ]
    """

    pdf_path = Path(pdf_path)

    pages = []
    name = document_name if document_name else pdf_path.name

    try:
        extracted_pages = _extract_pages_with_pdfium(pdf_path, name)
    except Exception:
        extracted_pages = _extract_pages_with_pdfplumber(pdf_path, name)

    link_text = "\n".join(page["text"] for page in extracted_pages[:2])
    research_link = infer_research_link(link_text, name)

    for page in extracted_pages:
        page["source_label"] = research_link["label"]
        page["source_url"] = research_link["url"]
        pages.append(page)

    return pages
