"use client";

import { useState } from "react";
import { SearchResponse } from "@/types/api";
import { searchBooks } from "@/lib/api";

export function useSearch() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function search(query: string) {
    setLoading(true);
    setError(null);

    try {
      const result = await searchBooks(query);
      setData(result);
    } catch {
      setError("Search failed.");
    } finally {
      setLoading(false);
    }
  }

  return {
    loading,
    error,
    data,
    search,
  };
}