import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Props {
  intent: string;
  semanticDescription: string;
  referenceBooks: string[];
}

export function IntentCard({
  intent,
  semanticDescription,
  referenceBooks,
}: Props) {
  return (
    <Card className="rounded-3xl border-0 shadow-sm">

      <CardContent className="space-y-6 p-6">

        <div>

          <p className="mb-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
            Intent
          </p>

          <Badge className="rounded-full">
            {intent}
          </Badge>

        </div>

        <div>

          <p className="mb-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
            Reference
          </p>

          <p className="text-sm leading-7">

            {referenceBooks.length
              ? referenceBooks.join(", ")
              : "None"}

          </p>

        </div>

        <div>

          <p className="mb-2 text-xs font-medium uppercase tracking-widest text-zinc-500">
            Semantic Profile
          </p>

          <p className="text-sm leading-7 text-zinc-600">
            {semanticDescription}
          </p>

        </div>

      </CardContent>

    </Card>
  );
}