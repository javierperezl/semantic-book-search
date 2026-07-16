import axios from "axios";
import { DebugSearchResponse, SearchResponse } from "@/types/api";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export async function searchBooks(query: string): Promise<SearchResponse> {
  const response = await api.get<SearchResponse>("/search", {
    params: { query },
  });

  return response.data;
}

export async function searchBooksDebug(
  query: string,
): Promise<DebugSearchResponse> {
  const response = await api.get<DebugSearchResponse>("/search", {
    params: { query, debug: true },
  });

  return response.data;
}