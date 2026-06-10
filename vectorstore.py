"""
Shared ChromaDB vector store setup for The Unofficial Guide (Milestone 4).

Both embed_store.py (indexing) and retrieve.py (querying) open the collection
through get_collection() so they use the SAME embedding model and distance
metric. We use cosine distance so scores fall on an intuitive ~0 (identical)
to ~1 (unrelated) scale.
"""

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "chroma_db"          # gitignored local persistence
COLLECTION_NAME = "omscs_courses"
EMBED_MODEL = "all-MiniLM-L6-v2"   # matches planning.md Retrieval Approach

# One shared embedding function -> identical embeddings at index and query time.
_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBED_MODEL
)


def get_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection():
    """Open (or create) the course-chunk collection."""
    return get_client().get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embed_fn,
        metadata={"hnsw:space": "cosine"},
    )
