import {
  Calendar,
  User,
} from "lucide-react";

import { Progress } from "@/components/ui/progress";

import {
  Card,
  CardContent,
} from "@/components/ui/card";

import { Badge } from "@/components/ui/badge";

import { Book } from "@/types/api";

interface Props {
  book: Book;
}

export function BookCard({ book }: Props) {
  const score = Math.round(
    (book.semantic_score ?? 0) * 100
  );

  return (
    <Card className="group rounded-3xl border-0 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg">

      <CardContent className="space-y-6 p-6">

        <div className="space-y-2">

          <h3 className="line-clamp-2 text-xl font-semibold">
            {book.title}
          </h3>

          <div className="flex items-center gap-2 text-sm text-zinc-500">

            <User className="h-4 w-4" />

            {book.author ?? "Unknown"}

          </div>

          {book.year && (
            <div className="flex items-center gap-2 text-sm text-zinc-500">

              <Calendar className="h-4 w-4" />

              {book.year}

            </div>
          )}

        </div>

        <div className="space-y-2">

          <div className="flex justify-between text-sm">

            <span>Semantic Match</span>

            <span className="font-medium">
              {score}%
            </span>

          </div>

          <Progress value={score} />

        </div>

        {book.description && (
          <p className="line-clamp-5 text-sm leading-7 text-zinc-600">
            {book.description}
          </p>
        )}

        <div className="flex flex-wrap gap-2">

          {book.subjects
            .slice(0, 5)
            .map((subject) => (
              <Badge
                key={subject}
                variant="secondary"
                className="rounded-full"
              >
                {subject}
              </Badge>
            ))}

        </div>

      </CardContent>

    </Card>
  );
}