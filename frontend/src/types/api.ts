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