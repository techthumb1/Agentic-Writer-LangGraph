// frontend/app/layout.tsx (Fresh version)
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { auth } from "@/auth";
import Link from "next/link";

import "./globals.css";
import { Providers } from "./providers";
import { ThemeProvider } from "./theme-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Content Generation Platform",
  description: "AI-powered content creation platform.",
};

// Server-side navigation items for authenticated users
const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/generate", label: "Generate Content" },
  { href: "/content", label: "My Content" },
  { href: "/templates", label: "Templates" },
  { href: "/settings", label: "Settings" },
];

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <Providers>
            <nav className="bg-gray-800 text-white p-4 shadow-md">
              <div className="container mx-auto flex justify-between items-center">
                <Link
                  href="/"
                  className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600"
                >
                  AI Content Studio
                </Link>
                
                <div className="flex items-center space-x-6">
                  {session?.user && (
                    <div className="flex space-x-2">
                      {navItems.map(({ href, label }) => (
                        <Link
                          key={href}
                          href={href}
                          className="px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ease-in-out transform hover:bg-gray-700 hover:text-purple-300 hover:scale-105 active:scale-95 active:bg-purple-700"
                        >
                          {label}
                        </Link>
                      ))}
                    </div>
                  )}

                  <div className="flex items-center space-x-4">
                    {session?.user ? (
                      <>
                        <span className="text-sm text-gray-300">
                          Welcome, {String(session.user.name || session.user.email || 'User')}
                        </span>
                        <form action="/api/auth/signout" method="post">
                          <button
                            type="submit"
                            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors duration-200"
                          >
                            Sign Out
                          </button>
                        </form>
                      </>
                    ) : (
                      <Link
                        href="/auth/signin"
                        className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors duration-200"
                      >
                        Sign In
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            </nav>

            <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
              {children}
            </main>
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}