# Portafolio · Semantic Book Search

Buscador semántico de libros en lenguaje natural sobre la [Open Library
Search API](https://openlibrary.org/dev/docs/api/search). El usuario
describe lo que busca ("libros como *Atomic Habits* pero para negocios") y
el sistema entiende la intención, busca candidatos reales, los rerankea por
similitud semántica y devuelve una recomendación explicada — sin inventar
libros ni datos que no estén respaldados por lo recuperado.

## Cómo funciona

```
query del usuario
      │
      ▼
extract_intent (LLM)  →  intent, libro(s) de referencia, search_queries, semantic_description
      │
      ▼
build_search_context
  ├─ busca el libro de referencia real en Open Library (si el usuario mencionó uno)
  ├─ multi_search: ejecuta las search_queries en paralelo contra /search.json
  ├─ excluye el libro de referencia de los candidatos (ya lo conoce el usuario)
  ├─ rerank barato (título/autor/subjects, sin /works) para preseleccionar
  ├─ enriquece solo la preselección con /works.json (descripción + subjects)
  └─ rerank final con el profile completo
      │
      ▼
generate_answer (LLM)  →  recomendación + explicación, priorizando evidencia real
```

No usa un vector store ni memoria entre requests: cada búsqueda trae y
rankea su propio corpus desde Open Library en el momento. Es una decisión
de alcance, no una limitación técnica — ver `evals/` y la sección de
roadmap más abajo si se necesita escalar esto.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

Variables de entorno (todas opcionales salvo la primera):

| Variable | Default | Descripción |
|---|---|---|
| `OPENAI_API_KEY` | — | **Requerida.** Key de OpenAI. |
| `INTENT_MODEL` | `gpt-4.1-mini` | Modelo para extraer intención. |
| `GENERATION_MODEL` | `gpt-4.1-mini` | Modelo para redactar la recomendación. |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Modelo de `sentence-transformers` para el reranking. |
| `MAX_SEARCH_QUERIES` | `5` | Tope de queries generadas por el LLM de intención. |
| `LIMIT_PER_QUERY` | `8` | Resultados por query contra `/search.json`. |
| `MAX_CANDIDATES_TO_ENRICH` | `15` | Cuántos candidatos se enriquecen con `/works.json`. |
| `MAX_RESULTS_TO_GENERATE` | `5` | Cuántos resultados entran al prompt del LLM generador. |
| `MAX_RESULTS_TO_RETURN` | `15` | Cuántos resultados devuelve la API en total. |
| `OPENLIBRARY_USER_AGENT` | — | User-Agent identificando la app (requerido por Open Library en uso serio). |
| `REQUEST_TIMEOUT` | `10.0` | Timeout en segundos para llamadas HTTP externas. |

```bash
export OPENAI_API_KEY=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
export OPENLIBRARY_USER_AGENT="Portafolio-BookSearch/1.0"
```

## Uso

```bash
uvicorn app.main:app --reload
```

```bash
curl "http://localhost:8000/search?query=quiero+un+libro+como+Atomic+Habits+pero+para+negocios"
```

Respuesta (recortada):

```json
{
  "query": "...",
  "intent": { "intent": "find_similar_books", "reference_books": ["Atomic Habits"], "...": "..." },
  "results": [ { "title": "...", "author": "...", "subjects": ["..."], "semantic_score": 0.62 } ],
  "answer": "...",
  "grounded": true,
  "warnings": []
}
```

- `grounded`: heurística barata que marca `false` si la respuesta no
  menciona ninguno de los títulos recuperados (posible señal de alucinación).
- `warnings`: detalle de por qué `grounded` dio `false`, si aplica.

## Tests

```bash
pytest
```

Los tests de `openlibrary.py` usan [`respx`](https://lundberg.github.io/respx/)
para mockear HTTP — no requieren conexión real ni credenciales.

## Estructura

```
app/
  config.py           # Settings vía variables de entorno
  models.py            # Modelos Pydantic (Intent, Book, SearchResponse)
  llm.py               # Extracción de intención + validación/reintento
  openlibrary.py       # Cliente async de /search y /works
  semantic_profile.py  # Limpieza de subjects + construcción de profiles
  retriever.py         # Orquesta la recuperación en dos etapas
  reranker.py          # Embeddings + cosine similarity + cache en memoria
  generator.py         # Prompt final + chequeo de grounding
  main.py              # Endpoint FastAPI
tests/                 # Unit tests (mockeados, sin red)
evals/                 # Eval de relevancia semántica vs keyword search (LLM-juez)
```

## Roadmap / limitaciones conocidas

- **Cache de embeddings en memoria de proceso**: no persiste entre
  reinicios ni se comparte entre workers. Si esto corre con más de un
  worker o en producción, migrar a Redis o similar.
- **Comparación de modelos** (OpenAI vs Ollama/Gemma local vs Gemini):
  hoy el proveedor de LLM está fijo a OpenAI en `llm.py`/`generator.py`.
  Para comparar limpio, extraer una interfaz mínima
  (`generate(prompt) -> str`) con un adaptador por proveedor.
- **`evals/eval_relevance.py`** es un punto de partida, no una suite
  exhaustiva: correr con más queries representativas antes de sacar
  conclusiones de un solo run.
- Sin persistencia ni logging estructurado más allá de lo que da FastAPI/uvicorn.
