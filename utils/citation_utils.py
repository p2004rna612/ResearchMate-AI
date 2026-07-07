"""
citation_utils.py

Helpers for creating research-friendly citation links from uploaded documents.
"""

import re
from urllib.parse import quote_plus


DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
ARXIV_PATTERN = re.compile(
    r"(?:arxiv\s*:\s*)?(\d{4}\.\d{4,5}(?:v\d+)?)",
    re.IGNORECASE
)


def _clean_doi(doi):
    return doi.rstrip(".,);]")


def infer_research_link(text, document_name):
    """
    Infer the best external research link for a document.

    Preference order:
    1. DOI URL
    2. arXiv URL
    3. Google Scholar search URL
    """

    doi_match = DOI_PATTERN.search(text or "")
    if doi_match:
        doi = _clean_doi(doi_match.group(0))
        return {
            "label": "DOI",
            "url": f"https://doi.org/{doi}",
        }

    arxiv_match = ARXIV_PATTERN.search(text or "")
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
        return {
            "label": "arXiv",
            "url": f"https://arxiv.org/abs/{arxiv_id}",
        }

    query = quote_plus(document_name)
    return {
        "label": "Google Scholar",
        "url": f"https://scholar.google.com/scholar?q={query}",
    }


def format_citation(chunk):
    citation = f"{chunk['document']} (Page {chunk['page']})"
    source_url = chunk.get("source_url")
    source_label = chunk.get("source_label", "Research link")

    if source_url:
        citation = f"{citation} - [{source_label}]({source_url})"

    return citation
