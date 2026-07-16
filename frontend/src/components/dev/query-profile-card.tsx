import { Fingerprint } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Intent, TraceReferenceBook } from "@/types/api";

interface Props {
  intent: Intent;
  queryProfile?: string | null;
  referenceBook?: TraceReferenceBook | null;
}

export function QueryProfileCard({ intent, queryProfile, referenceBook }: Props) {
  return (
    <Card className="rounded-3xl border-0 shadow-sm">
      <CardContent className="space-y-5 p-6">

        <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
          <Fingerprint className="h-4 w-4" />
          Intent &amp; query profile
        </p>

        <div className="flex flex-wrap items-center gap-2">
          <Badge className="rounded-full">{intent.intent}</Badge>

          {referenceBook && (
            <Badge
              variant={referenceBook.found ? "default" : "destructive"}
              className="rounded-full"
            >
              {referenceBook.found
                ? `ref: ${referenceBook.title}`
                : `ref not found: ${referenceBook.requested}`}
            </Badge>
          )}
        </div>

        <div>
          <p className="mb-1 text-xs font-medium text-zinc-500">
            Semantic description (LLM)
          </p>
          <p className="text-sm leading-6 text-zinc-600">
            {intent.semantic_description}
          </p>
        </div>

        <div>
          <p className="mb-1 text-xs font-medium text-zinc-500">
            Query profile (what actually gets embedded)
          </p>
          <p className="rounded-xl bg-zinc-50 p-3 font-mono text-xs leading-5 text-zinc-700">
            {queryProfile || "—"}
          </p>
        </div>

      </CardContent>
    </Card>
  );
}
