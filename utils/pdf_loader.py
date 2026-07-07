"""
pdf_loader.py

Responsible for:
- Reading PDF files
- Extracting text page by page
- Preserving document metadata
"""

from pathlib import Path
import pdfplumber

from utils.citation_utils import infer_research_link


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

    with pdfplumber.open(pdf_path) as pdf:

        extracted_pages = []

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()

            # Skip empty pages
            if not text or not text.strip():
                continue

            extracted_pages.append(
                {
                    "document": document_name if document_name else pdf_path.name,
                    "page": page_number,
                    "text": text.strip(),
                    "source_id": (
                        f"{Path(document_name).stem if document_name else pdf_path.stem}"
                        f"_page_{page_number}"
                    ),
                }
            )

    name = document_name if document_name else pdf_path.name
    link_text = "\n".join(page["text"] for page in extracted_pages[:2])
    research_link = infer_research_link(link_text, name)

    for page in extracted_pages:
        page["source_label"] = research_link["label"]
        page["source_url"] = research_link["url"]
        pages.append(page)

    return pages
