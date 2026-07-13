# Development Guide

This document defines how future development should be performed.

---

# Main Principle

The production pipeline must remain stable.

Research and experiments must happen outside the production pipeline whenever possible.

```
Production
        │
        ├──────── Stable
        │
        ▼
Experiments
        │
        ▼
If improvement is validated
        │
        ▼
Merge into production
```

---

# Workflow

Every new idea follows the same process.

```
Idea

↓

Experiment

↓

Evaluation

↓

Comparison

↓

Decision

↓

Merge
```

---

# Pull Requests

Every PR should answer

- What changed?
- Why?
- What metric improved?
- How was it evaluated?

---

# Branch Strategy

```
main

Stable production code


experiment/*

Research


feature/*

New features


fix/*

Bug fixes
```

---

# Coding Rules

## Keep functions small

Prefer

- one responsibility
- easy to test
- easy to replace

---

## Providers

Never import OpenAI directly outside

```
providers/
```

---

## Prompts

Never hardcode prompts.

Always place them inside

```
prompts/
```

---

## Config

Never hardcode

- models
- providers
- thresholds
- limits

Everything configurable belongs in

```
config.py
```

---

## Evaluations

Never evaluate manually.

Whenever possible

Create

- dataset
- metric
- report

inside

```
evals/
```

---

# Experiment Lifecycle

```
Implement

↓

Run benchmark

↓

Generate report

↓

Compare baseline

↓

Keep

or

Discard
```

---

# Baseline

Current production baseline

Intent

- OpenAI

Embeddings

- all-MiniLM-L6-v2

Generation

- OpenAI

Retrieval

- Open Library Search
- Open Library Works enrichment
- Two-stage reranking

---

# Future Experiments

## Intent

- Gemini
- Ollama
- Claude

---

## Embeddings

- OpenAI
- bge
- e5
- Nomic
- jina

---

## Generation

- GPT
- Gemini
- Ollama

---

## Retrieval

- Better search queries
- Better reranking
- Better enrichment

---

## Evaluation

- Human evaluation
- LLM Judge
- Precision metrics
- Latency
- Cost

---

# Definition of Done

A contribution is complete only if

- code works
- tests pass
- evaluation executed
- report generated
- documentation updated