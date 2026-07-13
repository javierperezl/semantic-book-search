# Backend Architecture

## Goal

Transform a natural language query into grounded book recommendations using Open Library as the only source of truth.

---

# Pipeline

```
Natural Language Query
        │
        ▼
Intent Extraction
        │
        ▼
Search Query Generation
        │
        ▼
Open Library Search
        │
        ▼
Candidate Books
        │
        ▼
Book Profile Construction
        │
        ▼
Cheap Semantic Reranking
        │
        ▼
Top-N Candidates
        │
        ▼
Metadata Enrichment (/works)
        │
        ▼
Book Profile Reconstruction
        │
        ▼
Final Semantic Reranking
        │
        ▼
Grounded Generation
        │
        ▼
API Response
```

---

# Modules

## main.py

FastAPI application.

Responsibilities

- startup
- routes
- orchestration

---

## providers/

Provider abstraction layer.

Contains interchangeable implementations for

- Intent
- Embeddings
- Generation

The application depends only on interfaces.

---

## openlibrary.py

Open Library client.

Responsibilities

- search
- work enrichment
- deduplication

---

## retriever.py

Retrieval pipeline.

Responsibilities

- reference book lookup
- candidate retrieval
- cheap rerank
- enrichment
- final rerank

---

## semantic_profile.py

Creates semantic representations used by embeddings.

Responsibilities

- clean metadata
- remove noisy subjects
- build query profile
- build book profile

---

## reranker.py

Computes embedding similarity.

Responsibilities

- encode query
- encode books
- cosine similarity
- ranking

---

## generator.py

Grounded generation.

Responsibilities

- choose books
- build generation context
- grounding verification
- call generation provider

---

## prompts/

Prompt templates only.

No application logic.

---

## config.py

Centralized configuration.

Environment variables.

---

## models.py

Shared Pydantic models.

---

## evals/

Offline evaluation framework.

Independent from production pipeline.

---

# Design Principles

- Provider pattern
- Dependency inversion
- Modular prompts
- Easy experimentation
- Easy benchmarking
- Easy model replacement
- Grounded generation
- Source of truth is Open Library

---

# Request Flow

```
HTTP Request

↓

Intent Provider

↓

Retriever

↓

Embedding Provider

↓

Generation Provider

↓

HTTP Response
```

---

# Future Extension Points

Intent

- Gemini
- Claude
- Ollama

Embeddings

- OpenAI
- BAAI
- Nomic
- e5
- bge

Generation

- Gemini
- Ollama
- Claude

Evaluation

- LLM Judges
- Human Evaluation
- Statistical Metrics

No core business logic should change when adding a new provider.