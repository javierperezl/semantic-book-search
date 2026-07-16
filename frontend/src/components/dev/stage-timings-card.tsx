import { Timer } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { StageTiming } from "@/types/api";

interface Props {
  timings: StageTiming[];
}

const STAGE_LABELS: Record<string, string> = {
  intent_extraction: "Intent extraction (LLM)",
  reference_book_lookup: "Reference book lookup",
  openlibrary_search: "Open Library search",
  cheap_rerank: "Cheap rerank (stage 1)",
  enrich_works: "Enrich with /works",
  final_rerank: "Final rerank (stage 3)",
  generation: "Answer generation (LLM)",
};

export function StageTimingsCard({ timings }: Props) {
  const total = timings.reduce((sum, t) => sum + t.duration_ms, 0);

  return (
    <Card className="rounded-3xl border-0 shadow-sm">
      <CardContent className="space-y-4 p-6">

        <div className="flex items-center justify-between">
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
            <Timer className="h-4 w-4" />
            Stage timings
          </p>
          <p className="text-sm font-semibold">
            {(total / 1000).toFixed(2)}s total
          </p>
        </div>

        <ol className="space-y-2">
          {timings.map((t) => {
            const pct = total > 0 ? (t.duration_ms / total) * 100 : 0;

            return (
              <li key={t.stage} className="flex items-baseline justify-between gap-4 text-sm">
                <span className="text-zinc-700">
                  {STAGE_LABELS[t.stage] ?? t.stage}
                </span>
                <span className="whitespace-nowrap font-mono text-zinc-500">
                  {t.duration_ms.toFixed(0)} ms · {pct.toFixed(0)}%
                </span>
              </li>
            );
          })}
        </ol>

      </CardContent>
    </Card>
  );
}
