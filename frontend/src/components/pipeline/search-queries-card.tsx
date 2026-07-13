import { Card, CardContent } from "@/components/ui/card";

interface Props {
  queries: string[];
}

export function SearchQueriesCard({
  queries,
}: Props) {
  return (
    <Card className="rounded-3xl border-0 shadow-sm">

      <CardContent className="space-y-4 p-6">

        <p className="text-xs font-medium uppercase tracking-widest text-zinc-500">
          Generated Queries
        </p>

        {queries.map((query) => (
          <div
            key={query}
            className="rounded-xl border bg-zinc-50 px-4 py-3 text-sm"
          >
            {query}
          </div>
        ))}

      </CardContent>

    </Card>
  );
}