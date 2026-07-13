import { Skeleton } from "@/components/ui/skeleton";

export function Loading() {
  return (
    <div className="space-y-5">

      <Skeleton className="h-36 rounded-2xl" />

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">

        <Skeleton className="h-64 rounded-2xl" />

        <Skeleton className="h-64 rounded-2xl" />

        <Skeleton className="h-64 rounded-2xl" />

      </div>

    </div>
  );
}