import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Help Center | AI Content Studio',
  description: 'Find answers to common questions and get support for AI Content Studio.',
};

export default function HelpCenterPage() {
  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Help Center
          </h1>
          <p className="text-xl text-gray-300">
            Find answers to common questions and get support for AI Content Studio.
          </p>
        </div>
        
        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
          <div className="text-center text-gray-300">
            <h2 className="text-2xl font-semibold mb-4">Coming Soon</h2>
            <p>
              We are working hard to bring you this feature. Check back soon for updates!
            </p>
            <div className="flex justify-center">
              <Link
                href="/"
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300"
              >
                Back to Home
              </Link>
            </div>
            </div>
          </div>
        </div>
      </div>
  );
}
