'use client';

import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function HomePage() {
  return (
    <section className="flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-6 text-center">
      <header className="max-w-4xl">
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6 text-gray-900">
          Unleash Your Content Superpower with AI
        </h1>
        <p className="text-xl text-gray-600 mb-10 leading-relaxed">
          Generate high-quality, customized content across various formats and styles — tailored to your needs.
          From blog posts to research summaries, let our AI agents do the heavy lifting.
        </p>
      </header>

      <div className="flex flex-wrap justify-center gap-4">
        <Link href="/generate" passHref>
          <Button
            size="lg"
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-full shadow-md transition-all duration-300"
          >
            Start Generating Now
          </Button>
        </Link>
        <Link href="/templates" passHref>
          <Button
            size="lg"
            variant="outline"
            className="border-purple-500 text-purple-600 hover:bg-purple-50 border-2 font-semibold px-8 py-3 rounded-full shadow-md transition-all duration-300"
          >
            Explore Templates
          </Button>
        </Link>
      </div>

      <footer className="mt-12 text-gray-500 text-sm">
        <p>Your ultimate platform for AI-driven content creation.</p>
        {/* Future: Add testimonials, logos, or feature highlights */}
      </footer>
    </section>
  );
}
