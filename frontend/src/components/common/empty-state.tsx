import { Search } from "lucide-react";

export function EmptyState() {
  return (
    <div className="rounded-3xl border border-dashed bg-white px-10 py-20 text-center">

      <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-zinc-100">

        <Search className="h-7 w-7 text-zinc-500" />

      </div>

      <h2 className="text-2xl font-semibold">
        Semantic Book Search
      </h2>

      <p className="mx-auto mt-3 max-w-xl text-zinc-500">
        Search naturally. The system understands your intent,
        retrieves books from Open Library and reranks them
        using semantic embeddings.
      </p>

    </div>
  );
}