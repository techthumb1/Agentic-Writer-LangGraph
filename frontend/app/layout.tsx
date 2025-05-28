import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link"; // For navigation links
import { Button } from "@/components/ui/button"; // Shadcn Button

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Content Generation Platform",
  description: "Monetizable AI-powered content creation platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {/* Simple Navigation Bar */}
        <nav className="bg-gray-800 text-white p-4 shadow-md">
          <div className="container mx-auto flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                AI Content Studio
            </Link>
            <div className="space-x-4">
              <Link href="/generate" passHref>
                <Button variant="ghost" className="text-white hover:bg-gray-700">Generate Content</Button>
              </Link>
              <Link href="/content" passHref>
                <Button variant="ghost" className="text-white hover:bg-gray-700">My Content</Button>
              </Link>
              <Link href="/templates" passHref>
                <Button variant="ghost" className="text-white hover:bg-gray-700">Templates</Button>
              </Link>
              <Link href="/settings" passHref>
                <Button variant="outline" className="text-white border-white hover:bg-white hover:text-gray-800">Settings</Button>
              </Link>
              {/* Future: Add Auth buttons like Login/Logout */}
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="container mx-auto p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
