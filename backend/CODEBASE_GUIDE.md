# Codebase Guide

This document is intended for new contributors.

Read this before modifying the project.

---

# Project Philosophy

This project separates the pipeline into independent stages.

Each stage has a single responsibility.

```
Intent

↓

Retrieval

↓

Semantic Ranking

↓

Generation

↓

Evaluation
```

Every stage should be replaceable without affecting the rest of the system.

---

# Folder Structure

```
app/

config.py

main.py

models.py

openlibrary.py

retriever.py

semantic_profile.py

reranker.py

generator.py

providers/

prompts/

evals/
```

---

# main.py

Application entry point.

Responsibilities

- initialize providers
- API routes
- orchestration

Should remain small.

---

# config.py

Reads environment variables.

Should never contain business logic.

---

# models.py

Contains shared Pydantic models.

Only data definitions.

---

# providers/

Implements dependency inversion.

The application never depends directly on OpenAI or SentenceTransformers.

Instead it depends on interfaces.

Example

```
IntentProvider

↓

OpenAIIntentProvider

↓

GeminiIntentProvider

↓

OllamaIntentProvider
```

The same applies to

- embeddings
- generation

---

# prompts/

Contains only prompts.

No Python logic.

No API calls.

No business rules.

---

# retriever.py

Core retrieval pipeline.

Responsible for

- retrieving candidates
- enrichment
- reranking orchestration

Should never call the LLM directly.

---

# semantic_profile.py

Transforms structured metadata into natural language profiles suitable for embedding models.

Responsible for

- cleaning
- deduplication
- profile generation

---

# reranker.py

Pure semantic ranking.

Should not know anything about Open Library.

Only compares vectors.

---

# generator.py

Uses retrieved evidence to build the final recommendation.

Responsible for

- selecting context
- grounding verification
- generation

Should not retrieve books.

---

# openlibrary.py

Single place responsible for external Open Library communication.

No semantic logic should exist here.

---

# evals/

Independent evaluation framework.

Production code must never depend on evals.

---

# Tests

tests/

Contains unit tests only.

Evaluation experiments belong inside evals/.

---

# Development Rules

When adding a new LLM

Only create

```
providers/intent/

or

providers/generation/
```

No changes should be required elsewhere.

---

When adding a new embedding model

Only implement

```
EmbeddingProvider
```

Everything else should continue working.

---

When changing prompts

Only modify

```
prompts/
```

Never modify application logic.

---

When adding experiments

Use

```
evals/
```

Never mix experimental code with production code.

---

# Goal

Keep the production pipeline

- modular
- reproducible
- testable
- benchmarkable
- easy to extend