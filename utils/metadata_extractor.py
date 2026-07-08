"""
metadata_extractor.py

Extracts common research-paper metadata from loaded document text.
"""

import re
from pathlib import Path

from utils.citation_utils import DOI_PATTERN


UNKNOWN_VALUE = "Not found"

VENUE_PATTERNS = [
    r"\bproceedings\b",
    r"\bconference\b",
    r"\bjournal\b",
    r"\btransactions\b",
    r"\bworkshop\b",
    r"\bsymposium\b",
    r"\bACM\b",
    r"\bIEEE\b",
    r"\bNeurIPS\b",
    r"\bICLR\b",
    r"\bICML\b",
    r"\bACL\b",
    r"\bEMNLP\b",
    r"\bCVPR\b",
    r"\barXiv\b",
]


def _clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip(" -,:;")


def _clean_doi(doi):
    return doi.rstrip(".,);]")


def _compact_lines(text):
    lines = []

    for line in (text or "").splitlines():
        line = _clean_text(line)

        if not line:
            continue

        if len(line) < 3:
            continue

        lines.append(line)

    return lines


def _first_match(pattern, text, flags=re.IGNORECASE):
    match = re.search(pattern, text or "", flags)
    return _clean_text(match.group(1)) if match else ""


def _extract_title(lines, document_name):
    skip_patterns = [
        r"^abstract\b",
        r"^keywords?\b",
        r"^introduction\b",
        r"^arxiv\b",
        r"^doi\b",
    ]

    for index, line in enumerate(lines[:12]):
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue

        if DOI_PATTERN.search(line):
            continue

        if 8 <= len(line) <= 180 and len(line.split()) >= 3:
            next_line = lines[index + 1] if index + 1 < len(lines) else ""

            if (
                next_line
                and 4 <= len(next_line) <= 80
                and len(next_line.split()) <= 5
                and not any(
                    re.search(pattern, next_line, re.IGNORECASE)
                    for pattern in skip_patterns
                )
                and "@" not in next_line
            ):
                return f"{line} {next_line}"

            return line

    return Path(document_name).stem.replace("_", " ").replace("-", " ").title()


def _extract_authors(lines, title):
    author_indicators = [
        r"\b(university|institute|department|college|school|laboratory|lab)\b",
        r"\b@[A-Za-z0-9.-]+\b",
        r"\b\d{4}\b",
        r"\babstract\b",
        r"\bkeywords?\b",
    ]

    for line in lines[1:12]:
        if line and line in title:
            continue

        if any(re.search(pattern, line, re.IGNORECASE) for pattern in author_indicators):
            continue

        has_name_separator = "," in line or " and " in line.lower()
        has_multiple_names = len(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", line)) >= 1
        has_compact_pdf_names = len(re.findall(r"[A-Z][a-z]+[A-Z][a-z]+", line)) >= 2

        if 5 <= len(line) <= 220 and (
            has_name_separator
            or has_multiple_names
            or has_compact_pdf_names
        ):
            return line

    return ""


def _extract_year(text):
    years = re.findall(r"\b(19[5-9]\d|20[0-4]\d)\b", text or "")
    return years[0] if years else ""


def _extract_keywords(text):
    keywords = _first_match(
        r"\b(?:key\s*words|keywords|index terms)\s*[:\-]?\s*(.+?)(?:\n\s*\n|\n(?:doi|1\.?\s*introduction|introduction)\b|\s+doi\s*:|\n[A-Z][A-Z\s]{5,}\n|$)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not keywords:
        return ""

    keywords = re.sub(r"\s*\.\s*$", "", keywords)
    keywords = re.sub(r"\s+", " ", keywords)
    parts = [
        _clean_text(part)
        for part in re.split(r",|;|\u2022", keywords)
        if _clean_text(part)
    ]

    return ", ".join(parts[:12])


def _extract_abstract(text):
    abstract = _first_match(
        r"\babstract\s*[:\-]?\s*(.+?)(?:\n\s*(?:key\s*words|keywords|index terms|1\.?\s*introduction|introduction)\b|$)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not abstract:
        return ""

    abstract = _clean_text(abstract)
    return abstract[:1200].rstrip()


def _extract_venue(lines):
    combined_patterns = re.compile("|".join(VENUE_PATTERNS), re.IGNORECASE)

    for line in lines[:40]:
        if combined_patterns.search(line) and len(line) <= 220:
            return line

    return ""


def extract_document_metadata(pages, document_name):
    """
    Extract metadata fields from the first pages of a loaded document.

    The function intentionally uses conservative heuristics so document
    processing works without an additional LLM or network call.
    """

    first_pages_text = "\n".join(page.get("text", "") for page in pages[:3])
    lines = _compact_lines(first_pages_text)

    doi_match = DOI_PATTERN.search(first_pages_text)
    doi = _clean_doi(doi_match.group(0)) if doi_match else ""

    title = _extract_title(lines, document_name)

    metadata = {
        "document": document_name,
        "title": title,
        "authors": _extract_authors(lines, title),
        "year": _extract_year(first_pages_text),
        "doi": doi,
        "venue": _extract_venue(lines),
        "keywords": _extract_keywords(first_pages_text),
        "abstract": _extract_abstract(first_pages_text),
    }

    for key, value in metadata.items():
        if key == "document":
            continue

        metadata[key] = value if value else UNKNOWN_VALUE

    return metadata
