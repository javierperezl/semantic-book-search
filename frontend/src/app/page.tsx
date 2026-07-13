"use client";

import { PageContainer } from "@/components/layout/page-container";
import { SearchInput } from "@/components/search/search-input";

import { Loading } from "@/components/common/loading";
import { EmptyState } from "@/components/common/empty-state";

import { AnswerCard } from "@/components/results/answer-card";
import { ResultsGrid } from "@/components/results/results-grid";

import { useSearch } from "@/hooks/use-search";

import { PipelineCard } from "@/components/pipeline/pipeline-card";

import { ExamplePrompts } from "@/components/search/example-prompts";

export default function HomePage() {
  const {
    loading,
    data,
    error,
    search,
  } = useSearch();

  return (
    <PageContainer>

      <div className="mx-auto max-w-7xl space-y-14">

        <div className="space-y-4 text-center">

          <h1 className="text-6xl font-semibold tracking-tight">
            Semantic Book Search
          </h1>

          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Search books using LLMs, semantic embeddings and Open Library.
          </p>

        </div>

        <SearchInput
          loading={loading}
          onSearch={search}
          initialQuery={data?.query}
        />

        <ExamplePrompts
          onSelect={search}
        />

        {error && (
          <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-600">
            {error}
          </div>
        )}

        {loading && <Loading />}

        {!loading && !data && (
          <EmptyState />
        )}

        {!loading && data && (
          <div className="space-y-16">

              <AnswerCard
                  answer={data.answer}
              />

              <ResultsGrid
                  books={data.results}
              />

              <PipelineCard
                  data={data}
              />

          </div>
        )}

      </div>

    </PageContainer>
  );
}