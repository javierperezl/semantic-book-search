import { siteConfig } from "@/config/site";

export function Navbar() {
  return (
    <header className="border-b">
      <div className="mx-auto flex h-16 max-w-7xl items-center px-6">
        <h1 className="text-lg font-semibold">
          {siteConfig.name}
        </h1>
      </div>
    </header>
  );
}