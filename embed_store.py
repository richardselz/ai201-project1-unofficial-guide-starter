"""
Milestone 4 — Embed chunks and load them into ChromaDB.

Reads chunks.csv (from chunk.py), embeds each chunk with all-MiniLM-L6-v2,
and stores it in a persistent ChromaDB collection with source metadata
(source_file, course, section, chunk_index) for later attribution.

Run once after chunking:  python embed_store.py
"""

import csv
from pathlib import Path

from vectorstore import COLLECTION_NAME, get_client, get_collection

CHUNKS_CSV = Path("chunks.csv")


def main():
    rows = list(csv.DictReader(CHUNKS_CSV.open(encoding="utf-8")))

    # Rebuild from scratch so re-runs don't duplicate or stale-out chunks.
    client = get_client()
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    collection = get_collection()

    collection.add(
        ids=[r["id"] for r in rows],
        documents=[r["text"] for r in rows],
        metadatas=[
            {
                "source_file": r["source_file"],
                "course": r["course"],
                "section": r["section"],
                "chunk_index": int(r["chunk_index"]),
            }
            for r in rows
        ],
    )

    print(f"embedded + stored {collection.count()} chunks "
          f"in ChromaDB collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()
