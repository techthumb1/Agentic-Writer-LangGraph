// frontend/app/layout.tsx (Responsive version with professional header & footer)
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { auth } from "@/auth";
import Link from "next/link";
import { ResponsiveNavigation } from "@/components/ResponsiveNavigation"
import "./globals.css";
import { Providers } from "./providers";
import { ThemeProvider } from "./theme-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Content Generation Platform",
  description: "AI-powered content creation platform.",
};

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
          <Providers session={session}>
            {/* Responsive Header */}
            <header className="bg-gray-800 text-white shadow-lg sticky top-0 z-50">
              <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                  {/* Logo */}
                  <div className="flex-shrink-0">
                    <Link
                      href="/"
                      className="text-xl sm:text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 hover:from-purple-300 hover:to-pink-500 transition-all duration-200"
                    >
                      AI Content Studio
                    </Link>
                  </div>

                  {/* Desktop Navigation */}
                  <div className="hidden lg:block">
                    {session?.user && (
                      <div className="flex items-center space-x-1">
                        {[
                          { href: "/dashboard", label: "Dashboard" },
                          { href: "/generate", label: "Generate" },
                          { href: "/content", label: "My Content" },
                          { href: "/templates", label: "Templates" },
                          { href: "/settings", label: "Settings" },
                        ].map(({ href, label }) => (
                          <Link
                            key={href}
                            href={href}
                            className="px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 ease-in-out transform hover:bg-gray-700 hover:text-purple-300 hover:scale-105 active:scale-95 active:bg-purple-700"
                          >
                            {label}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* User Actions */}
                  <div className="flex items-center space-x-3">
                    {session?.user ? (
                      <>
                        {/* User Welcome - Hidden on small screens */}
                        <span className="hidden sm:block text-sm text-gray-300 max-w-32 sm:max-w-none truncate">
                          Welcome, {String(session.user.name || session.user.email || 'User').split(' ')[0]}
                        </span>
                        
                        {/* Sign Out Button */}
                        <form action={async () => {
                          "use server";
                          const { signOut } = await import("@/auth");
                          await signOut({ redirectTo: "/" });
                        }}>
                          <button
                            type="submit"
                            className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-gray-800"
                          >
                            Sign Out
                          </button>
                        </form>
                      </>
                    ) : (
                      <Link
                        href="/auth/signin"
                        className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-800"
                      >
                        Sign In
                      </Link>
                    )}

                    {/* Mobile Menu Button */}
                    {session?.user && (
                      <ResponsiveNavigation />
                    )}
                  </div>
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
              {children}
            </main>

            {/* Professional Footer */}
            <footer className="bg-gray-900 text-gray-300 border-t border-gray-800">
              <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                  {/* Company Info */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white">AI Content Studio</h3>
                    <p className="text-sm text-gray-400 leading-relaxed">
                      Empowering creators with cutting-edge AI technology to generate high-quality, 
                      customized content across various formats and styles.
                    </p>
                    <div className="flex space-x-4">
                      <a href="#" className="text-gray-400 hover:text-purple-400 transition-colors">
                        <span className="sr-only">Twitter</span>
                        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                        </svg>
                      </a>
                      <a href="#" className="text-gray-400 hover:text-purple-400 transition-colors">
                        <span className="sr-only">GitHub</span>
                        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                          <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                        </svg>
                      </a>
                      <a href="#" className="text-gray-400 hover:text-purple-400 transition-colors">
                        <span className="sr-only">LinkedIn</span>
                        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                      </a>
                    </div>
                  </div>

                  {/* Product */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white">Product</h3>
                    <ul className="space-y-2">
                      <li><Link href="/generate" className="text-sm hover:text-purple-400 transition-colors">Content Generator</Link></li>
                      <li><Link href="/templates" className="text-sm hover:text-purple-400 transition-colors">Templates</Link></li>
                      <li><Link href="/dashboard" className="text-sm hover:text-purple-400 transition-colors">Analytics</Link></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">API Access</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Integrations</a></li>
                    </ul>
                  </div>

                  {/* Support */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white">Support</h3>
                    <ul className="space-y-2">
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Help Center</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Documentation</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Contact Support</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Community</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">System Status</a></li>
                    </ul>
                  </div>

                  {/* Company */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white">Company</h3>
                    <ul className="space-y-2">
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">About Us</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Careers</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Press Kit</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Privacy Policy</a></li>
                      <li><a href="#" className="text-sm hover:text-purple-400 transition-colors">Terms of Service</a></li>
                    </ul>
                  </div>
                </div>

                {/* Bottom Section */}
                <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center">
                  <div className="text-sm text-gray-400">
                    © 2025 AI Content Studio. All rights reserved.
                  </div>
                  <div className="mt-4 md:mt-0 flex space-x-6">
                    <a href="#" className="text-sm text-gray-400 hover:text-purple-400 transition-colors">Privacy</a>
                    <a href="#" className="text-sm text-gray-400 hover:text-purple-400 transition-colors">Terms</a>
                    <a href="#" className="text-sm text-gray-400 hover:text-purple-400 transition-colors">Cookies</a>
                  </div>
                </div>
              </div>
            </footer>
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}