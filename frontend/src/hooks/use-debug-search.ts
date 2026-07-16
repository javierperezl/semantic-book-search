"use client";

import { useState } from "react";
import { isAxiosError } from "axios";
import { DebugSearchResponse } from "@/types/api";
import { searchBooksDebug } from "@/lib/api";

export function useDebugSearch() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<DebugSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function search(query: string) {
    setLoading(true);
    setError(null);

    try {
      const result = await searchBooksDebug(query);
      setData(result);
    } catch (err) {
      console.error("Debug search failed:", err);

      if (isAxiosError(err)) {
        if (err.response) {
          setError(err.response.data?.detail ?? `Search failed (${err.response.status}).`);
        } else {
          setError("Could not reach the search API. Is the backend running?");
        }
      } else {
        setError("Search failed.");
      }
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
