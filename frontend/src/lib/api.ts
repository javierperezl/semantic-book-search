import axios from "axios";
import { SearchResponse } from "@/types/api";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export async function searchBooks(query: string): Promise<SearchResponse> {
  const response = await api.get<SearchResponse>("/search", {
    params: { query },
  });

  return response.data;
}