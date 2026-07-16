import { Library } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { TraceQueryResult } from "@/types/api";

interface Props {
  queries: TraceQueryResult[];
  totalCandidates: number;
}

export function RetrievalCard({ queries, totalCandidates }: Props) {
  return (
    <Card className="rounded-3xl border-0 shadow-sm">
      <CardContent className="space-y-4 p-6">

        <div className="flex items-center justify-between">
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
            <Library className="h-4 w-4" />
            Open Library retrieval
          </p>
          <p className="text-sm font-semibold">
            {totalCandidates} unique candidates
          </p>
        </div>

        <ul className="space-y-2">
          {queries.map((q) => (
            <li
              key={q.query}
              className="flex items-center justify-between gap-4 text-sm"
            >
              <span className="font-mono text-xs text-zinc-700">
                “{q.query}”
              </span>

              {q.failed ? (
                <Badge variant="destructive" className="rounded-full">
                  failed
                </Badge>
              ) : (
                <span className="whitespace-nowrap text-zinc-500">
                  {q.returned} results
                </span>
              )}
            </li>
          ))}
        </ul>

      </CardContent>
    </Card>
  );
}
