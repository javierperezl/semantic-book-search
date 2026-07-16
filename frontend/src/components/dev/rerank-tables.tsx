import { ArrowDown, ArrowUp, ListOrdered, Minus } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { TraceCheapCandidate, TraceFinalCandidate } from "@/types/api";

function RankDelta({ cheap, final }: { cheap?: number | null; final: number }) {
  if (cheap == null) {
    return <span className="text-zinc-400">new</span>;
  }

  const delta = cheap - final;

  if (delta > 0) {
    return (
      <span className="inline-flex items-center gap-0.5 text-emerald-600">
        <ArrowUp className="h-3 w-3" />
        {delta}
      </span>
    );
  }

  if (delta < 0) {
    return (
      <span className="inline-flex items-center gap-0.5 text-red-500">
        <ArrowDown className="h-3 w-3" />
        {-delta}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center text-zinc-400">
      <Minus className="h-3 w-3" />
    </span>
  );
}

interface CheapProps {
  candidates: TraceCheapCandidate[];
}

export function CheapRerankCard({ candidates }: CheapProps) {
  const selectedCount = candidates.filter((c) => c.selected_for_enrichment).length;

  return (
    <Card className="rounded-3xl border-0 shadow-sm">
      <CardContent className="space-y-4 p-6">

        <div className="flex items-center justify-between">
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
            <ListOrdered className="h-4 w-4" />
            Stage 1 · Cheap rerank
          </p>
          <p className="text-sm text-zinc-500">
            top {selectedCount} of {candidates.length} pass to enrichment
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b text-xs uppercase tracking-wider text-zinc-400">
                <th className="py-2 pr-4 font-medium">#</th>
                <th className="py-2 pr-4 font-medium">Book</th>
                <th className="py-2 text-right font-medium">Score</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c, i) => {
                const isCutoff =
                  !c.selected_for_enrichment &&
                  (i === 0 || candidates[i - 1].selected_for_enrichment);

                return (
                  <tr
                    key={c.key ?? `${c.title}-${c.rank}`}
                    className={
                      (isCutoff ? "border-t-2 border-dashed border-zinc-300 " : "") +
                      (c.selected_for_enrichment ? "" : "text-zinc-400")
                    }
                  >
                    <td className="py-1.5 pr-4 font-mono text-xs">{c.rank}</td>
                    <td className="py-1.5 pr-4">
                      {c.title ?? "Untitled"}
                      {c.author && (
                        <span className="text-zinc-400"> — {c.author}</span>
                      )}
                    </td>
                    <td className="py-1.5 text-right font-mono text-xs">
                      {c.score.toFixed(4)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

      </CardContent>
    </Card>
  );
}

interface FinalProps {
  candidates: TraceFinalCandidate[];
}

export function FinalRerankCard({ candidates }: FinalProps) {
  return (
    <Card className="rounded-3xl border-0 shadow-sm">
      <CardContent className="space-y-4 p-6">

        <div className="flex items-center justify-between">
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
            <ListOrdered className="h-4 w-4" />
            Stage 3 · Final rerank (after enrichment)
          </p>
          <p className="text-sm text-zinc-500">
            Δ = positions moved vs. stage 1
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b text-xs uppercase tracking-wider text-zinc-400">
                <th className="py-2 pr-4 font-medium">#</th>
                <th className="py-2 pr-4 font-medium">Book</th>
                <th className="py-2 pr-4 text-right font-medium">Final</th>
                <th className="py-2 pr-4 text-right font-medium">Cheap</th>
                <th className="py-2 pr-4 text-right font-medium">Δ</th>
                <th className="py-2 text-right font-medium">Desc</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.key ?? `${c.title}-${c.final_rank}`}>
                  <td className="py-1.5 pr-4 font-mono text-xs">{c.final_rank}</td>
                  <td className="py-1.5 pr-4">
                    {c.title ?? "Untitled"}
                    {c.author && (
                      <span className="text-zinc-400"> — {c.author}</span>
                    )}
                  </td>
                  <td className="py-1.5 pr-4 text-right font-mono text-xs">
                    {c.final_score.toFixed(4)}
                  </td>
                  <td className="py-1.5 pr-4 text-right font-mono text-xs text-zinc-400">
                    {c.cheap_score != null ? c.cheap_score.toFixed(4) : "—"}
                  </td>
                  <td className="py-1.5 pr-4 text-right text-xs">
                    <RankDelta cheap={c.cheap_rank} final={c.final_rank} />
                  </td>
                  <td className="py-1.5 text-right text-xs">
                    {c.description_added ? "✓" : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </CardContent>
    </Card>
  );
}
