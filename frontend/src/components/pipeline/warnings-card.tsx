import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Props {
  grounded: boolean;
  warnings: string[];
}

export function WarningsCard({
  grounded,
  warnings,
}: Props) {
  return (
    <Card className="rounded-3xl border-0 shadow-sm">

      <CardContent className="space-y-6 p-6">

        <div>

          <p className="mb-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
            Grounding
          </p>

          <Badge
            variant={
              grounded
                ? "default"
                : "destructive"
            }
            className="rounded-full"
          >
            {grounded
              ? "Grounded"
              : "Not grounded"}
          </Badge>

        </div>

        <div>

          <p className="mb-3 text-xs font-medium uppercase tracking-widest text-zinc-500">
            Warnings
          </p>

          {warnings.length === 0 ? (
            <p className="text-sm text-zinc-500">
              No warnings.
            </p>
          ) : (
            <div className="space-y-3">
              {warnings.map((warning) => (
                <div
                  key={warning}
                  className="rounded-xl border bg-zinc-50 p-3 text-sm leading-6"
                >
                  {warning}
                </div>
              ))}
            </div>
          )}

        </div>

      </CardContent>

    </Card>
  );
}