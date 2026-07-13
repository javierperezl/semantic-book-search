import { BrainCircuit } from "lucide-react";

import { SearchResponse } from "@/types/api";

import { IntentCard } from "./intent-card";
import { SearchQueriesCard } from "./search-queries-card";
import { WarningsCard } from "./warnings-card";

interface Props {
  data: SearchResponse;
}

export function PipelineCard({ data }: Props) {
  return (
    <section className="space-y-6">

      <div className="flex items-center gap-3">

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-100">

          <BrainCircuit className="h-5 w-5" />

        </div>

        <div>

          <h2 className="text-3xl font-semibold tracking-tight">
            AI Pipeline
          </h2>

          <p className="text-zinc-500">
            What happened behind the scenes.
          </p>

        </div>

      </div>

      <div className="grid gap-6 lg:grid-cols-3">

        <IntentCard
          intent={data.intent.intent}
          semanticDescription={data.intent.semantic_description}
          referenceBooks={data.intent.reference_books}
        />

        <SearchQueriesCard
          queries={data.intent.search_queries}
        />

        <WarningsCard
          grounded={data.grounded}
          warnings={data.warnings}
        />

      </div>

    </section>
  );
}