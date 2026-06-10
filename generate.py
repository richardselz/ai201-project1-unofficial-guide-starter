"""
Milestone 5 — Grounded answer generation.

answer(query) retrieves the top-k chunks (retrieve.py), passes ONLY those
chunks to Groq's llama-3.3-70b-versatile as context, and returns a grounded
answer plus programmatic source attribution.

Grounding is enforced two ways:
  1. System prompt: answer ONLY from the provided sources; if they are
     insufficient, return a fixed refusal string (no outside knowledge).
  2. Structure: temperature=0, sources are numbered and labelled with their
     course, and attribution is built from the retrieved chunks in code -- so
     citations can't be hallucinated by the model.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from retrieve import TOP_K, retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
REFUSAL = "I don't have enough information to answer that based on the course documents."

SYSTEM_PROMPT = (
    "You are a factual assistant that answers questions about Georgia Tech "
    "OMSCS courses. Use ONLY the numbered sources provided in the user message. "
    "Do not use any prior or outside knowledge. If the sources do not contain "
    f'enough information to answer, reply with exactly: "{REFUSAL}" '
    "When you do answer, state which course(s) the information came from."
)

_client = Groq(api_key=os.environ["GROQ_API_KEY"])


def _format_context(chunks):
    return "\n\n".join(
        f"[Source {i}: {c['course']} — {c['section']}]\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    )


def answer(query, k=TOP_K):
    """Return {'answer', 'sources', 'chunks'} for a user query."""
    chunks = retrieve(query, k=k)
    user_msg = f"Sources:\n{_format_context(chunks)}\n\nQuestion: {query}"

    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    text = resp.choices[0].message.content.strip()

    # Programmatic attribution: unique courses among retrieved chunks, in rank
    # order. Suppressed when the model refused (nothing was actually used).
    refused = REFUSAL[:30].lower() in text.lower()
    sources = []
    if not refused:
        for c in chunks:
            if c["course"] not in sources:
                sources.append(c["course"])

    return {"answer": text, "sources": sources, "chunks": chunks}


def _demo():
    queries = [
        "Who is the Head TA of CS 6035?",
        "What Apple hardware is not supported in CS 6210?",
        "Which course teaches the need for a trusted computing base?",  # failure case
        "How many of the courses are considered foundational?",          # Q4 partial/refusal
        "What is the tuition for the OMSCS program?",                    # clearly out-of-scope
    ]
    for q in queries:
        result = answer(q)
        print("\n" + "=" * 72)
        print("Q:", q)
        print("A:", result["answer"])
        print("Sources:", result["sources"] or "(none — refused)")


if __name__ == "__main__":
    _demo()
