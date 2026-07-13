# Semantic Book Search Roadmap

## Current Status

The MVP is functional.

Implemented components:

- ✅ FastAPI backend
- ✅ Next.js frontend
- ✅ Intent extraction
- ✅ Open Library retrieval
- ✅ Metadata enrichment (/works)
- ✅ Semantic profiles
- ✅ Embedding reranking
- ✅ Grounded generation
- ✅ Provider architecture
- ✅ Prompt separation
- ✅ Evaluation framework skeleton
- ✅ Basic tests
- ✅ CI

The focus now shifts from **building** to **evaluating and improving**.

---

# Phase 1 — Baseline (Current)

Objective

Establish a stable production baseline.

Current configuration

Intent

- OpenAI

Embeddings

- Sentence Transformers
- all-MiniLM-L6-v2

Generation

- OpenAI

Retrieval

- Open Library Search
- Open Library Works
- Two-stage reranking

Deliverable

Stable MVP.

Status

✅ Completed

---

# Phase 2 — Embedding Experiments

Goal

Determine which embedding model produces the best semantic ranking.

Candidates

- all-MiniLM-L6-v2
- OpenAI text-embedding-3-small
- OpenAI text-embedding-3-large
- bge-large
- bge-small
- multilingual-e5
- Nomic
- jina embeddings

Measure

- Retrieval relevance
- Ranking quality
- Latency
- Cost

Deliverable

Embedding benchmark report.

---

# Phase 3 — Intent Experiments

Goal

Compare LLMs for query understanding.

Candidates

- GPT
- Gemini
- Ollama
- Claude

Measure

- Intent correctness
- Search query quality
- Semantic description quality
- Latency
- Cost

Deliverable

Intent benchmark report.

---

# Phase 4 — Generation Experiments

Goal

Compare recommendation quality.

Candidates

- GPT
- Gemini
- Ollama

Measure

- Grounding
- Explanation quality
- Hallucination rate
- Readability
- Latency

Deliverable

Generation benchmark report.

---

# Phase 5 — Prompt Experiments

Goal

Improve prompting.

Variables

- Retrieval prompt
- Intent prompt
- Generation prompt
- Context formatting

Measure

- Same metrics as above

Deliverable

Prompt comparison report.

---

# Phase 6 — Retrieval Experiments

Possible improvements

- Better search query generation
- Reciprocal Rank Fusion
- Hybrid search
- Metadata weighting
- Better enrichment
- Query expansion

Measure

Overall retrieval quality.

---

# Phase 7 — Evaluation

Automatic benchmark.

Metrics

- Relevance
- Grounding
- Latency
- Cost
- Human score
- LLM Judge score

Output

Markdown report

CSV

JSON

Charts

---

# Phase 8 — Production

Final polish.

Tasks

- Better UI
- Deploy backend
- Deploy frontend
- Monitoring
- Logging
- Error handling
- Documentation
- Demo

Deliverable

Public production MVP.

---

# Long-Term Ideas

- Vector database
- Multi-agent retrieval
- Personalized recommendations
- Reading history
- User profiles
- RAG over additional book sources
- Citation extraction
- Recommendation explanations
- Streaming responses
- Conversation memory