# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

The OMSCS program at Georgia Institute of Technology (GaTech) has pages for all of their online courses. These pages provide details about such as the overview, course goals, and before taking this class (suggested background knowledge).

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | OMSCS | URL | https://omscs.gatech.edu/cs-6035-introduction-information-security |
| 2 | OMSCS | URL | https://omscs.gatech.edu/cs-6150-computing-good |
| 3 | OMSCS | URL | https://omscs.gatech.edu/cs-6200-introduction-operating-systems |
| 4 | OMSCS | URL | https://omscs.gatech.edu/cs-6210-advanced-operating-systems |
| 5 | OMSCS | URL | https://omscs.gatech.edu/cs-6211-system-design-cloud-computing |
| 6 | OMSCS | URL | https://omscs.gatech.edu/cs-6238-secure-computer-systems |
| 7 | OMSCS | URL | https://omscs.gatech.edu/cs-6250-computer-networks |
| 8 | OMSCS | URL | https://omscs.gatech.edu/cs-6260-applied-cryptography |
| 9 | OMSCS | URL | https://omscs.gatech.edu/cs-6261-security-incident-response |
| 10 | OMSCS | URL | https://omscs.gatech.edu/cs-6262-network-security |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
The chunking is done by splitting each page at its `h4` section headers (detected dynamically, not a fixed list), so every section — Overview, Before Taking This Class, Academic Integrity, Course Goals, etc. — becomes its own chunk. Each section body is capped at 180 words; if a section is longer it is split further with a one-sentence overlap.


**Overlap:**
The majority of the data will be chunked into sizes that will not require overlap. The sections also do not require any overlap as they are self-contained units. 

**Why these choices fit your documents:**
The reasoning is that this provides a great separation between each area domain and it provides for smaller chunks to be created all while still supplying the course number and title in every chunk. 

**Final chunk count:**
The total chunks for this project was 61 from the 10 documents provided, with 5 to 8 chunks per document/course.

---

## Sample Chunks

**1.** *(source: cs-6035.txt — Instructional Team)*
> CS 6035: Introduction to Information Security — Instructional Team
> Wenke Lee Creator, Instructor Chris Taylor Head TA

**2.** *(source: cs-6210.txt — Before Taking This Class..., 182 words)*
> CS 6210: Advanced Operating Systems — Before Taking This Class... Suggested Background Knowledge Students are expected to have completed an undergraduate OS course, or have industry experience... You will need a machine which supports VT-X or AMD-V. i.e. machines that run on i3, i5 or, i7 and later Intel processors... *(truncated)*

**3.** *(source: cs-6238.txt — Course Goals)*
> CS 6238: Secure Computer Systems — Course Goals ... Demonstrate the need for a trusted computing base (TCB) and how it helps protect resources in a computer system. Analyze how hardware supported memory protection enables isolation of TCB and of untrusted programs...

**4.** *(source: cs-6250.txt — Before Taking This Class...)*
> CS 6250: Computer Networks — Before Taking This Class... Suggested Background Knowledge ... Can you explain the main distinction between TCP and UDP? ... Do you understand the three way handshake of TCP? ...

**5.** *(source: cs-6262.txt — Instructional Team)*
> CS 6262: Network Security — Instructional Team
> Wenke Lee Creator, Instructor Melissa Chen Head TA

---

## Embedding Model

**Model used:**
The embedding model used was `all-MiniLM-L6-v2` since it was recommended in the project and it is a free local model that uses limited resources.

**Production tradeoff reflection:**
In production if this was a critical application then a high-fidelity embedding model should be utilized to hopefully create more accurate query retrieval. In production we could use a larger embedding model and then not require overlaps within our retrieval and chunking processes.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt forces the model to answer only from retrieved context:

> "You are a factual assistant that answers questions about Georgia Tech OMSCS courses. Use ONLY the numbered sources provided in the user message. Do not use any prior or outside knowledge. If the sources do not contain enough information to answer, reply with exactly: 'I don't have enough information to answer that based on the course documents.' When you do answer, state which course(s) the information came from."

Grounding is enforced by three mechanisms: (1) only the top-5 retrieved chunks are passed in, each labelled `[Source N: Course — Section]` — the model never sees the full corpus; (2) generation runs at `temperature=0` to prevent drift; (3) a mandatory refusal string is returned when context is insufficient (e.g. the out-of-scope tuition question).

**How source attribution is surfaced in the response:**

Attribution is built programmatically in `generate.py` — after generation, the code collects the unique courses among the retrieved chunks and returns them, shown in the UI's "Retrieved from" box. This guarantees citations can't be hallucinated. It can over-list (name a retrieved course the answer didn't use), so the answer prose names the specific course while "Retrieved from" shows everything consulted.


---

## Example Responses

Verbatim system output (answer text + the UI's "Retrieved from" list):

**1. Grounded answer**
> **Q:** Who is the Head TA of CS 6035?
> **A:** The Head TA of CS 6035 is Chris Taylor. This information came from Source 1: CS 6035: Introduction to Information Security — Instructional Team.
> **Retrieved from:** • CS 6035: Introduction to Information Security

**2. Grounded answer**
> **Q:** What Apple hardware is not supported in CS 6210?
> **A:** The Apple M1/M2 hardware is not supported in CS 6210, according to Source 1: CS 6210: Advanced Operating Systems — Before Taking This Class.
> **Retrieved from:** • CS 6210: Advanced Operating Systems

**3. Out-of-scope query (refusal)**
> **Q:** What is the tuition for the OMSCS program?
> **A:** I don't have enough information to answer that based on the course documents.
> **Retrieved from:** (none — not enough information in the course documents)

---

## Query Interface

A Gradio web app (`app.py`), launched with `python app.py` and opened at `http://localhost:7860`.

- **Inputs:** a "Your question" free-text box, plus a checkbox toggle ("Use a provided evaluation question") that swaps the box for a dropdown of the six evaluation questions.
- **Outputs:** an **Answer** box (the grounded response) and a **Retrieved from** box (the source course pages consulted).

**Sample interaction transcript:**
```
[Your question] What Apple hardware is not supported in CS 6210?
[Answer]        The Apple M1/M2 hardware is not supported in CS 6210,
                according to Source 1: CS 6210: Advanced Operating Systems
                — Before Taking This Class.
[Retrieved from] • CS 6210: Advanced Operating Systems
```

---

## Retrieval Test Results

Three queries run through the retriever (top-k = 5, cosine distance; lower = more similar):

**Query 1 — "What Apple hardware is not supported in CS 6210?"** *(course-filtered → cs-6210.txt)*
| Rank | Distance | Chunk (course · section) |
|------|----------|--------------------------|
| 1 | 0.405 | CS 6210 · Before Taking This Class |
| 2 | 0.537 | CS 6210 · Before Taking This Class |
| 3 | 0.561 | CS 6210 · Course Content |

*Why relevant:* The query names "CS 6210", so metadata filtering restricts results to that course. The #1 chunk is CS 6210's "Before Taking This Class" section, which contains the hardware/VM requirements including the "Apple M1/M2 is currently not supported" line — a direct match.

**Query 2 — "Which course recommends understanding the three-way handshake of TCP?"** *(no filter)*
| Rank | Distance | Chunk (course · section) |
|------|----------|--------------------------|
| 1 | 0.497 | CS 6250 · Before Taking This Class |
| 2 | 0.594 | CS 6250 · Instructional Team |
| 3 | 0.595 | CS 6262 · Sample Syllabi |

*Why relevant:* The #1 chunk is CS 6250's background-knowledge section, which literally lists "Do you understand the three way handshake of TCP?" Semantic search matched it despite the query writing "three-way" and the document writing "three way" — embeddings beating exact keyword matching.

**Query 3 — "Which course teaches the need for a trusted computing base (TCB)?"** *(no filter)*
| Rank | Distance | Chunk (course · section) |
|------|----------|--------------------------|
| 1 | 0.402 | CS 6238 · Course Goals |
| 2 | 0.408 | CS 6250 · Sample Syllabi |
| 3 | 0.422 | CS 6262 · Sample Syllabi |

*Why relevant:* The #1 chunk is CS 6238's Course Goals, which states the goal to "demonstrate the need for a trusted computing base (TCB)" — a direct match to the query.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Who is the Head TA of CS 6035? | Chris Taylor | "Chris Taylor" — cited CS 6035 Instructional Team | Relevant (course-filtered) | Accurate |
| 2 | What courses does Wenke Lee teach? | CS 6035 and CS 6262 | "CS 6262 and CS 6035" — both retrieved at ranks #1–2 | Relevant | Accurate |
| 3 | What Apple hardware is not supported in CS 6210? | Apple M1/M2 | "Apple M1/M2" — cited CS 6210 | Relevant (course-filtered) | Accurate |
| 4 | How many of the courses are considered foundational? | Out-of-scope (not in corpus) | Noted CS 6150 is "not foundational," then declined to give a count | Off-target (correct — no such fact) | Appropriate refusal |
| 5 | Which course recommends understanding the three-way handshake of TCP? | CS 6250 | "CS 6250" — top chunk dist 0.497 | Relevant | Accurate |
| 6 | Which course teaches the need for a trusted computing base (TCB)? | CS 6238 | "CS 6238" — top chunk dist 0.402 | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** 
"Which courses are not foundational?" (a harder probe — all 6 planned eval questions passed, so per the milestone's guidance I stress-tested an adjacent aggregation query). Ground truth: two courses, CS 6150 and CS 6261, both state this in their page text.

**What the system returned:** 
It named only CS 6150 (plus CS 8903-C4G from within that chunk) and silently omitted CS 6261, with no signal the answer was incomplete.

**Root cause (retrieval stage / top-k recall):** 
This is a list-all / aggregation query. CS 6261's "not foundational" chunk ranked below the top-5, so it was never passed to the LLM. Generation answered correctly from what it received — the failure is upstream in retrieval recall, and metadata filtering can't help since no course is named. (This is the aggregation risk noted in planning.md Anticipated Challenges.)

**What you would change:** 
Add hybrid/BM25 keyword search so the literal phrase "not foundational" is matched across all documents regardless of embedding rank, or raise k / detect "list-all" intent to widen recall for aggregation queries.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The spec document helped to make sure that we did not diverge from the original plan while implementing the plan. Since we did some research into how much chunking and how it would be done prior to implementation it provided us with less cases to test to find a useful setup. 

**One way your implementation diverged from the spec, and why:**
Originally we had a plan to have four chunks per document, but once we started workig on the implementation with the help of Claude we found that it was beneficial to chunk on the `h4` header tags.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
Initially I told Claude to chunk the data based on the 4 sections that I thought would be useful for the data that would need to be generated.
- *What it produced:*
Claude took that idea, but found that it would be more beneficial to utilize the `h4` headers as a natural split instead of an arbitrary 4 sections that I had initially told it.
- *What I changed or overrode:*
This instance I did not need to correct Claudes implementation as it was a lot more sound then the initial implementation.

**Instance 2**

- *What I gave the AI:*
I asked the AI to provide me with the head ta of CS 6035.
- *What it produced:*
It produced an incorrect result because it did not find the context within CS 6035.
- *What I changed or overrode:*
I proposed the change to have metadata filtering on a regex based "CS XXXX" pattern that makes it so that if it is seen the query will only look at results within that courses document chunks.

---

## Acknowledgments

- **Claude (Anthropic)** — used throughout this project as a coding and reasoning partner: pressure-testing planning decisions, generating and debugging the ingestion, chunking, embedding, retrieval, and generation code, and helping diagnose issues along the way.
- **Groq** — for the free, fast inference API (`llama-3.3-70b-versatile`) that powers the grounded answer generation in this system.