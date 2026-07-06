"""
pdf_loader.py

Responsible for:
- Reading PDF files
- Extracting text page by page
- Preserving document name and page numbers
"""

from pathlib import Path
import pdfplumber


def load_pdf(pdf_path):
    """
    Load a PDF and return structured page data.

    Returns:
        list of dictionaries:
        [
            {
                "document": "sample.pdf",
                "page": 1,
                "text": "..."
            }
        ]
    """

    pdf_path = Path(pdf_path)

    pages = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()

            if text:

                pages.append(
                    {
                        "document": pdf_path.name,
                        "page": page_number,
                        "text": text.strip()
                    }
                )

    return pages