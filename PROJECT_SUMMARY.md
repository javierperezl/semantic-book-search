# Project Summary: Semantic Book Search

Semantic Book Search is a sophisticated book recommendation system that leverages Large Language Models (LLMs) and semantic embeddings to provide grounded, intent-aware book recommendations using **Open Library** as the primary source of truth.

## 🎯 Core Objective
The system moves beyond simple keyword matching. It focuses on understanding the **user's underlying intent** to recommend books based on semantic profiles, ensuring every recommendation is backed by real data to eliminate LLM hallucinations.

---

## 🏗️ System Architecture

The project follows a decoupled architecture with a Python backend and a TypeScript frontend.

### 1. Backend: The Intelligence Pipeline (FastAPI)
The backend implements a multi-stage pipeline to transform a natural language query into a grounded response:

1.  **Intent Extraction:** An LLM analyzes the query to produce an `Intent` object containing:
    *   Optimized search queries.
    *   Reference books mentioned by the user.
    *   A semantic description of the desired result.
2.  **Candidate Retrieval (The Retriever):**
    *   Fetches initial candidates from Open Library.
    *   **Two-Stage Reranking Strategy:**
        *   *Cheap Rerank:* Fast filtering using basic metadata.
        *   *Enrichment:* Fetches full metadata (`/works`) only for the top-N candidates.
        *   *Final Rerank:* High-precision ranking using semantic embeddings on complete profiles.
3.  **Grounded Generation:** A final LLM pass synthesizes the results into a natural language answer, citing specific evidence from the retrieved books.

#### Key Design Patterns:
*   **Provider Pattern:** Decouples the application logic from specific AI vendors. Providers for Intent, Embeddings, and Generation can be swapped (e.g., OpenAI $ightarrow$ Gemini/Ollama) without changing core business logic.
*   **Semantic Profiling:** Transforms raw, noisy Open Library data into clean "semantic profiles" (Title + Author + Cleaned Subjects + Description) to improve embedding accuracy.

### 2. Frontend: Visual Transparency (Next.js)
Built with **Next.js, Tailwind CSS, and shadcn/ui**, the frontend is designed to make the AI's reasoning visible:

*   **Interactive Search:** Clean interface with example prompts.
*   **Pipeline Visualization:** Includes a `PipelineCard` that reveals the internal steps (intent, search, reranking) taken to reach the result.
*   **Modern UI:** Responsive design utilizing a component-based architecture.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend Framework** | Python, FastAPI, Pydantic |
| **AI / ML** | OpenAI (Intent/Gen), Sentence Transformers (Embeddings) |
| **Data Source** | Open Library API |
| **Frontend Framework** | TypeScript, Next.js (App Router) |
| **Styling** | Tailwind CSS, shadcn/ui |
| **Evaluation** | Custom framework in `/backend/evals` for relevance and latency |

---

## 📂 Repository Structure

```text
semantic-book-search/
├── backend/
│   ├── app/                # Core logic (retriever, generator, profiles)
│   │   ├── providers/      # AI Provider implementations (Dependency Inversion)
│   │   └── prompts/        # Modular prompt templates
│   ├── evals/              # Evaluation framework for benchmarking models
│   └── tests/              # Unit and integration tests
├── frontend/
│   ├── src/
│   │   ├── components/     # UI Components (pipeline, results, search)
│   │   ├── hooks/          # Custom React hooks (e.g., useSearch)
│   │   └── lib/            # API clients and utilities
└── README.md               # Project overview
```

## 🚀 Key Highlights
- **Hallucination Prevention:** Every recommendation is grounded in Open Library data.
- **Efficiency:** The two-stage reranking optimizes API calls and latency.
- **Extensibility:** The provider architecture allows for effortless experimentation with different LLMs and embedding models.
