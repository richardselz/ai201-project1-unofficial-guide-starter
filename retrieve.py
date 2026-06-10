"""
Milestone 4 — Semantic retrieval over the course-chunk vector store.

retrieve(query, k=5) embeds the query with all-MiniLM-L6-v2 and returns the
top-k most similar chunks with their source metadata and cosine distance.

Stretch feature — course metadata filtering:
    If the query names a specific course (e.g. "CS 6035"), retrieval is
    restricted to that course's chunks. This fixes cross-course confusion,
    where near-identical sections (e.g. "Instructional Team") across the 10
    courses out-rank the correct one. Queries that don't name a course
    (e.g. "Which course teaches X?") search the whole corpus, as intended.
    Toggle with USE_METADATA_FILTER or the per-call metadata_filter arg.

Run directly to sanity-check retrieval on a few evaluation questions:
    python retrieve.py
"""

import re

from vectorstore import get_collection

TOP_K = 5                      # planning.md Retrieval Approach
USE_METADATA_FILTER = True     # global on/off switch for course filtering

# Matches "CS 6035", "cs6035", "CS  6035", etc.
COURSE_RE = re.compile(r"\bCS\s*(\d{4})\b", re.IGNORECASE)


def course_source(query):
    """Return the source_file a query targets (e.g. 'cs-6035.txt'), or None."""
    m = COURSE_RE.search(query)
    return f"cs-{m.group(1)}.txt" if m else None


def retrieve(query, k=TOP_K, metadata_filter=USE_METADATA_FILTER):
    """Return the top-k chunks for a query as a list of dicts.

    When metadata_filter is on and the query names a course, results are
    restricted to that course. If the filter matches no chunks (e.g. an
    unknown course number), we fall back to an unfiltered search.
    """
    collection = get_collection()
    where = None
    if metadata_filter:
        source = course_source(query)
        if source:
            where = {"source_file": source}

    res = collection.query(query_texts=[query], n_results=k, where=where)

    # Fallback: filtered to a course with no chunks -> search everything.
    if where and not res["ids"][0]:
        where = None
        res = collection.query(query_texts=[query], n_results=k)

    return [
        {"text": doc, "distance": dist,
         "source_file": meta["source_file"],
         "course": meta["course"], "section": meta["section"],
         "filtered_to": where["source_file"] if where else None}
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        )
    ]


def _demo():
    questions = [
        "Who is the Head TA of CS 6035?",
        "What Apple hardware is not supported in CS 6210?",
        "Which course recommends understanding the three-way handshake of TCP?",
        "Which course teaches the need for a trusted computing base?",
    ]
    for q in questions:
        results = retrieve(q)
        tag = (f"[filtered -> {results[0]['filtered_to']}]"
               if results and results[0]["filtered_to"] else "[no filter]")
        print("\n" + "=" * 72)
        print("Q:", q, tag)
        for i, r in enumerate(results, 1):
            print(f"  {i}. dist={r['distance']:.3f}  {r['course']} · {r['section']}")


if __name__ == "__main__":
    _demo()
