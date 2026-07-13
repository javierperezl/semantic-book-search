import { Book } from "@/types/api";

import { BookCard } from "./book-card";

interface Props {
  books: Book[];
}

export function ResultsGrid({
  books,
}: Props) {
  return (
    <section className="space-y-6">

      <div>

        <h2 className="text-3xl font-semibold tracking-tight">
          Retrieved Books
        </h2>

        <p className="mt-2 text-zinc-500">
          Ranked by semantic similarity.
        </p>

      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">

        {books.map((book) => (
          <BookCard
            key={book.key}
            book={book}
          />
        ))}

      </div>

    </section>
  );
}