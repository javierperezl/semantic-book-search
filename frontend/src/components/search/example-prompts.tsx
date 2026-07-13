interface Props {
  onSelect: (query: string) => void;
}

const prompts = [
  "Books like Atomic Habits but for business",
  "Books about entrepreneurship",
  "Machine learning for beginners",
  "Best negotiation books",
];

export function ExamplePrompts({ onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-3">
      {prompts.map((prompt) => (
        <button
          key={prompt}
          onClick={() => onSelect(prompt)}
          className="rounded-full border bg-white px-4 py-2 text-sm text-zinc-600 transition-all hover:border-zinc-900 hover:text-zinc-900"
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}