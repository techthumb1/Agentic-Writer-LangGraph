// frontend/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";

import "./globals.css";
import { Button } from "@/components/ui/button";
import { ReactQueryProvider } from "@/lib/react-query-provider";
import { ThemeProvider } from "./theme-provider"; // 👈 Wrap in NextThemes for future dark mode support

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Content Generation Platform",
  description: "Monetizable AI-powered content creation platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <ReactQueryProvider>
            <nav className="bg-gray-800 text-white p-4 shadow-md">
              <div className="container mx-auto flex justify-between items-center">
                <Link
                  href="/"
                  className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600"
                >
                  AI Content Studio
                </Link>
                <div className="space-x-4">
                  {[
                    { href: "/generate", label: "Generate Content" },
                    { href: "/content", label: "My Content" },
                    { href: "/templates", label: "Templates" },
                    { href: "/settings", label: "Settings" },
                  ].map(({ href, label }) => (
                    <Link key={href} href={href} passHref>
                      <Button
                        variant="ghost"
                        className="text-white hover:bg-gray-700"
                      >
                        {label}
                      </Button>
                    </Link>
                  ))}
                </div>
              </div>
            </nav>

            <main className="container mx-auto p-8">{children}</main>
          </ReactQueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
