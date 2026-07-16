"use client";

import { FormEvent, useEffect, useState } from "react";
import { Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Props {
  loading: boolean;
  onSearch: (query: string) => void;
  initialQuery?: string;
}

export function SearchInput({
  loading,
  onSearch,
  initialQuery = "",
}: Props) {
  const [query, setQuery] = useState(initialQuery);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  function submit(e: FormEvent) {
    e.preventDefault();

    if (!query.trim()) return;

    onSearch(query.trim());
  }

  return (
    <form
      onSubmit={submit}
      className="flex items-center gap-3 rounded-2xl border bg-white p-2 shadow-sm transition-all"
    >
      <Search className="ml-3 h-5 w-5 text-zinc-400" />

      <Input
        className="h-12 border-0 bg-transparent text-base shadow-none focus-visible:ring-0"
        placeholder="Describe the book you're looking for..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <Button
        // Base UI renderiza type="button" por defecto; sin esto el click
        // no dispara el onSubmit del form (solo funcionaba con Enter)
        type="submit"
        className="h-12 rounded-xl px-6"
        disabled={loading}
      >
        {loading ? "Searching..." : "Search"}
      </Button>
    </form>
  );
}