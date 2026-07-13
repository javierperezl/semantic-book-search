import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";

import "./globals.css";

export const metadata: Metadata = {
  title: "Semantic Book Search",
  description: "LLMs + Embeddings + Open Library",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
    >
      <body
        className={`${GeistSans.className} ${GeistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}