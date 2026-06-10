"""
Milestone 3 — Chunking for The Unofficial Guide.

Reads the structured documents/*.txt produced by ingest.py and splits each
into chunks following the planning.md Chunking Strategy:

  * One chunk per page section (the "## Heading" boundaries from ingest.py).
  * Every chunk is prefixed with the course number + title, so near-identical
    sections across the 10 courses stay distinguishable at retrieval time.
  * Soft cap of ~180 words/chunk (fits all-MiniLM-L6-v2's 256-token window).
    A longer section is split into sub-chunks with one sentence of overlap.
  * Trivially small sections (empty "Preview", a bare "Current Syllabus" link)
    are dropped.

Output: chunks.csv with one row per chunk + source metadata for Milestone 4.
"""

import csv
import re
from pathlib import Path

DOCS_DIR = Path("documents")
OUT_CSV = Path("chunks.csv")

MAX_WORDS = 180          # soft cap per chunk
MIN_BODY_WORDS = 3       # drop sections with less real content than this
OVERLAP_SENTENCES = 1    # sentence overlap when a long section is sub-split


def parse_sections(text):
    """Yield (course_title, section_heading, body) from one structured doc.

    The first line is '# <course title>'. Sections start at '## '. '### '
    subsection headings are folded into their parent section's body.
    """
    lines = text.splitlines()
    course_title = lines[0].lstrip("# ").strip() if lines else "Unknown Course"

    heading, body = None, []
    for line in lines[1:]:
        if line.startswith("## "):
            if heading is not None:
                yield course_title, heading, "\n".join(body).strip()
            heading, body = line[3:].strip(), []
        elif line.startswith("### "):
            body.append(line[4:].strip())   # keep subsection text, drop the ###
        elif heading is not None:
            body.append(line)
    if heading is not None:
        yield course_title, heading, "\n".join(body).strip()


def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def pack_sentences(sentences):
    """Pack sentences into ≤MAX_WORDS sub-chunks with sentence overlap."""
    chunks, current, count = [], [], 0
    for sent in sentences:
        n = len(sent.split())
        if current and count + n > MAX_WORDS:
            chunks.append(" ".join(current))
            current = current[-OVERLAP_SENTENCES:]          # carry overlap
            count = sum(len(s.split()) for s in current)
        current.append(sent)
        count += n
    if current:
        chunks.append(" ".join(current))
    return chunks


def chunk_text(course_title, heading, body):
    """Return a list of prefixed chunk strings for one section."""
    if len(body.split()) < MIN_BODY_WORDS:
        return []                                            # drop tiny sections
    prefix = f"{course_title} — {heading}"
    pieces = ([body] if len(body.split()) <= MAX_WORDS
              else pack_sentences(split_sentences(body)))
    return [f"{prefix}\n{piece}" for piece in pieces]


def main():
    rows = []
    for path in sorted(DOCS_DIR.glob("cs-*.txt")):
        text = path.read_text(encoding="utf-8")
        for course_title, heading, body in parse_sections(text):
            for i, chunk in enumerate(chunk_text(course_title, heading, body)):
                rows.append({
                    "id": f"{path.stem}-{heading.lower().replace(' ', '-')[:20]}-{i}",
                    "source_file": path.name,
                    "course": course_title,
                    "section": heading,
                    "chunk_index": i,
                    "word_count": len(chunk.split()),
                    "text": chunk,
                })

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} chunks to {OUT_CSV}")


if __name__ == "__main__":
    main()
