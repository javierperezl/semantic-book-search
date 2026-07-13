# Semantic Book Search

Semantic book recommendation system built on top of Open Library.

Instead of relying on keyword matching, the system understands the user's intent, retrieves candidate books from Open Library, enriches them with additional metadata, reranks them using semantic embeddings, and finally generates grounded recommendations with an LLM.

---

# Repository Structure

```
semantic-book-search/

├── backend/
│   ├── app/
│   ├── evals/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   └── package.json
│
└── README.md
```

---

# Architecture

```
User Query
      │
      ▼
Intent Extraction (LLM)
      │
      ▼
Search Query Generation
      │
      ▼
Open Library /search
      │
      ▼
Candidate Books
      │
      ▼
Cheap Semantic Reranking
      │
      ▼
Top-N
      │
      ▼
Open Library /works
      │
      ▼
Metadata Enrichment
      │
      ▼
Final Semantic Reranking
      │
      ▼
Grounded Generation
      │
      ▼
Recommendation + Evidence
```

---

# Main Components

Backend

- FastAPI
- Open Library client
- Intent extraction
- Semantic retrieval
- Embedding providers
- Generation providers
- Evaluation framework

Frontend

- Next.js
- Tailwind
- shadcn/ui
- Interactive pipeline visualization

---

# Features

- Semantic search
- Intent extraction
- Reference book understanding
- Metadata enrichment
- Semantic reranking
- Grounded recommendations
- Modular provider architecture
- Evaluation framework
- Modern UI

---

# Current Providers

Intent

- OpenAI

Embeddings

- Sentence Transformers

Generation

- OpenAI

The provider architecture allows additional implementations without changing the application logic.

---

# Evaluation

The repository includes an evaluation framework to compare:

- LLMs
- Embedding models
- Prompt versions
- Retrieval quality
- Grounding
- Latency

---

# Future Experiments

- OpenAI vs Gemini
- OpenAI vs Ollama
- MiniLM vs OpenAI Embeddings
- Different prompts
- Different reranking strategies
- Judge LLM evaluation
- Automatic benchmark reports

---

# Running

Backend

```bash
cd backend

source .venv/bin/activate

uvicorn app.main:app --reload
```

Frontend

```bash
cd frontend

npm run dev
```

---

# License

MIT