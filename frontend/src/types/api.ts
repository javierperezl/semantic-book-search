export interface Intent {
  intent: string;
  reference_books: string[];
  search_queries: string[];
  semantic_description: string;
}

export interface Book {
  title?: string;
  author?: string;
  year?: number;
  edition_count: number;
  subjects: string[];
  description?: string;
  ratings_average?: number;
  ratings_count?: number;
  readinglog_count?: number;
  key?: string;

  profile?: string;
  semantic_score?: number;
}

export interface SearchResponse {
  query: string;
  intent: Intent;
  results: Book[];
  answer: string;
  grounded: boolean;
  warnings: string[];
}

// --- Trace del pipeline (solo presente con /search?debug=true) ---

export interface StageTiming {
  stage: string;
  duration_ms: number;
}

export interface TraceQueryResult {
  query: string;
  returned: number;
  failed: boolean;
}

export interface TraceReferenceBook {
  requested: string;
  found: boolean;
  title?: string | null;
  author?: string | null;
  key?: string | null;
}

export interface TraceCheapCandidate {
  key?: string | null;
  title?: string | null;
  author?: string | null;
  rank: number;
  score: number;
  selected_for_enrichment: boolean;
}

export interface TraceFinalCandidate {
  key?: string | null;
  title?: string | null;
  author?: string | null;
  final_rank: number;
  final_score: number;
  cheap_rank?: number | null;
  cheap_score?: number | null;
  description_added: boolean;
}

export interface PipelineTrace {
  query_profile?: string | null;
  reference_book?: TraceReferenceBook | null;
  queries: TraceQueryResult[];
  total_candidates: number;
  cheap_rerank: TraceCheapCandidate[];
  final_rerank: TraceFinalCandidate[];
  timings: StageTiming[];
}

export interface DebugSearchResponse extends SearchResponse {
  trace: PipelineTrace;
}