import { Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface Props {
  answer: string;
}

export function AnswerCard({ answer }: Props) {
  return (
    <Card className="rounded-3xl border-0 shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-100">
            <Sparkles className="h-5 w-5" />
          </div>

          <CardTitle className="text-xl">
            Recommendation
          </CardTitle>
        </div>
      </CardHeader>

      <CardContent>
        <div className="prose prose-zinc max-w-none prose-headings:font-semibold prose-p:leading-8 prose-li:leading-8">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {answer}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  );
}