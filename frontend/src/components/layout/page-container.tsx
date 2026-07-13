interface Props {
  children: React.ReactNode;
}

export function PageContainer({ children }: Props) {
  return (
    <main className="min-h-screen bg-zinc-50">
      <div className="mx-auto max-w-7xl px-6 py-14 md:px-10">
        {children}
      </div>
    </main>
  );
}