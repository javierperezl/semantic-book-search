"use client";

import Link from "next/link";
import { FlaskConical } from "lucide-react";

import { PageContainer } from "@/components/layout/page-container";
import { SearchInput } from "@/components/search/search-input";
import { Loading } from "@/components/common/loading";

import { AnswerCard } from "@/components/results/answer-card";
import { StageTimingsCard } from "@/components/dev/stage-timings-card";
import { QueryProfileCard } from "@/components/dev/query-profile-card";
import { RetrievalCard } from "@/components/dev/retrieval-card";
import {
  CheapRerankCard,
  FinalRerankCard,
} from "@/components/dev/rerank-tables";

import { useDebugSearch } from "@/hooks/use-debug-search";

export default function DevPage() {
  const { loading, data, error, search } = useDebugSearch();

  return (
    <PageContainer>
      <div className="mx-auto max-w-7xl space-y-10">

        <div className="space-y-3 text-center">
          <h1 className="flex items-center justify-center gap-3 text-4xl font-semibold tracking-tight">
            <FlaskConical className="h-8 w-8 text-zinc-400" />
            Pipeline Inspector
          </h1>

          <p className="mx-auto max-w-2xl text-zinc-500">
            Run a search with tracing enabled and inspect every stage:
            retrieval, reranking, enrichment and latency.
          </p>

          <Link
            href="/"
            className="text-sm text-zinc-400 underline-offset-4 hover:underline"
          >
            ← back to user UI
          </Link>
        </div>

        <SearchInput
          loading={loading}
          onSearch={search}
          initialQuery={data?.query}
        />

        {error && (
          <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-600">
            {error}
          </div>
        )}

        {loading && <Loading />}

        {!loading && !data && (
          <p className="text-center text-zinc-400">
            Run a search to see the pipeline trace.
          </p>
        )}

        {!loading && data && (
          <div className="space-y-6">

            <div className="grid gap-6 lg:grid-cols-2">
              <StageTimingsCard timings={data.trace.timings} />
              <RetrievalCard
                queries={data.trace.queries}
                totalCandidates={data.trace.total_candidates}
              />
            </div>

            <QueryProfileCard
              intent={data.intent}
              queryProfile={data.trace.query_profile}
              referenceBook={data.trace.reference_book}
            />

            <CheapRerankCard candidates={data.trace.cheap_rerank} />

            <FinalRerankCard candidates={data.trace.final_rerank} />

            <AnswerCard answer={data.answer} />

          </div>
        )}

      </div>
    </PageContainer>
  );
}
