"""
Milestone 3 — Document Ingestion for The Unofficial Guide (OMSCS course pages).

Fetches each OMSCS course page, isolates the main <article>, strips
navigation / images / scripts, and writes structured plain text to
documents/<course-code>.txt with one "## Heading" per page section.

The structured output preserves the page's <h4> section boundaries so the
chunking step (chunk.py) can split cleanly on sections.
"""

import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString

# The 10 source documents from planning.md
URLS = [
    "https://omscs.gatech.edu/cs-6035-introduction-information-security",
    "https://omscs.gatech.edu/cs-6150-computing-good",
    "https://omscs.gatech.edu/cs-6200-introduction-operating-systems",
    "https://omscs.gatech.edu/cs-6210-advanced-operating-systems",
    "https://omscs.gatech.edu/cs-6211-system-design-cloud-computing",
    "https://omscs.gatech.edu/cs-6238-secure-computer-systems",
    "https://omscs.gatech.edu/cs-6250-computer-networks",
    "https://omscs.gatech.edu/cs-6260-applied-cryptography",
    "https://omscs.gatech.edu/cs-6261-security-incident-response",
    "https://omscs.gatech.edu/cs-6262-network-security",
]

OUT_DIR = Path("documents")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; UnofficialGuide/1.0; course project)"}

# Tags whose contents are noise — never include in the cleaned text.
SKIP_TAGS = {
    "script", "style", "img", "svg", "nav", "header", "footer",
    "figure", "figcaption", "form", "button", "noscript",
}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

# Some pages embed escaped tag text (e.g. "<head>", "<meta ...>") in the body;
# bs4 un-escapes it back into literal text. Drop tokens that are just a tag.
BARE_TAG = re.compile(r"^</?[a-zA-Z][^>]*>$")


def walk(node, out):
    """Recursively collect (kind, text) tokens in document order.

    kind is a heading tag name ('h4', 'h5', ...) or 'text'. Heading text is
    captured once (we don't recurse into headings); body text comes from
    leaf strings. SKIP_TAGS subtrees are dropped entirely (this is how
    images get stripped — see Q4 in planning.md).
    """
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text and not BARE_TAG.match(text):
                out.append(("text", text))
        elif child.name in SKIP_TAGS:
            continue
        elif child.name in HEADING_TAGS:
            out.append((child.name, child.get_text(" ", strip=True)))
        else:
            walk(child, out)


def clean_page(html):
    """Return (course_title, structured_markdown) from a course page's HTML."""
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article") or soup
    tokens = []
    walk(article, tokens)

    # The first h1 is the course title (e.g. "CS 6035: Introduction ...").
    title = next((t for kind, t in tokens if kind == "h1"), "Unknown Course")

    lines = [f"# {title}", ""]
    for kind, text in tokens:
        if kind == "h1":
            continue                      # already used as the document title
        elif kind == "h4":
            lines += ["", f"## {text}"]   # section boundary
        elif kind in ("h5", "h6"):
            lines.append(f"### {text}")   # subsection / instructor role
        else:
            lines.append(text)

    # Collapse runs of blank lines and trailing whitespace.
    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return title, md


def course_code(url):
    """Derive a short filename, e.g. 'cs-6035' from the URL slug."""
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    m = re.match(r"(cs-\d+)", slug)
    return m.group(1) if m else slug


def main():
    OUT_DIR.mkdir(exist_ok=True)
    for url in URLS:
        code = course_code(url)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        title, md = clean_page(resp.text)
        out_path = OUT_DIR / f"{code}.txt"
        out_path.write_text(md, encoding="utf-8")
        print(f"saved {out_path}  ({len(md.split())} words)  <- {title}")
        time.sleep(1)  # be polite to the server


if __name__ == "__main__":
    main()
