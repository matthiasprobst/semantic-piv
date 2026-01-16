import re

import pypdf
from rdflib import Graph

COMMENT_RE = re.compile(r'(?m)^\s*#.*\n?')  # full-line comments
TRAILING_WS_RE = re.compile(r'[ \t]+(?=\n)')  # trailing spaces
BLANK_LINES_RE = re.compile(r'\n{3,}')  # 3+ newlines -> 2
SPACE_AROUND_RE = re.compile(r'[ \t]{2,}')  # multiple spaces -> 1


def compact_turtle_file(ttl_path: str) -> str:
    """
    Parse Turtle and re-serialize + remove non-semantic noise (comments/whitespace).
    This preserves all RDF triples; ordering may change.
    """
    g = Graph()
    g.parse(ttl_path, format="turtle")

    # Re-serialize (rdflib already produces a relatively compact Turtle)
    ttl = g.serialize(format="turtle")

    # Ensure it's a str (rdflib sometimes returns bytes depending on version)
    if isinstance(ttl, (bytes, bytearray)):
        ttl = ttl.decode("utf-8", errors="replace")

    # Remove comments and whitespace noise (does NOT change RDF meaning)
    ttl = COMMENT_RE.sub("", ttl)
    ttl = TRAILING_WS_RE.sub("", ttl)
    ttl = BLANK_LINES_RE.sub("\n\n", ttl)
    ttl = SPACE_AROUND_RE.sub(" ", ttl)

    return ttl.strip() + "\n"


def compact_turtle_to_file(ttl_in: str, ttl_out: str) -> None:
    compact = compact_turtle_file(ttl_in)
    with open(ttl_out, "w", encoding="utf-8") as f:
        f.write(compact)


def pdf2text(pdf_path: str) -> str:
    """
    Extract text from PDF using PyMuPDF (fitz).
    """
    reader = pypdf.PdfReader(pdf_path)
    text = [page.extract_text() for page in reader.pages]
    return "\n".join(text)
