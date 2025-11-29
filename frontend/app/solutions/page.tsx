"use client"

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { 
  ArrowRight, 
  Users, 
  Building2, 
  FileText, 
  Lightbulb, 
  Target,
  Zap,
  Brain,
  Rocket
} from 'lucide-react';

export default function SolutionsPage() {
  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-6xl mx-auto text-white">
        {/* Page Header */}
        <header className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6">
            Solutions for Every 
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
              {" "}Content Need
            </span>
          </h1>
          <p className="text-xl text-gray-300 leading-relaxed max-w-3xl mx-auto">
            Discover how our AI-powered platform can transform your content creation process 
            across different industries and use cases.
          </p>
        </header>

        {/* Solutions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300 transform hover:scale-105">
            <div className="bg-purple-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <FileText className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-4 text-center">Content Marketing</h3>
            <p className="text-gray-300 mb-4 text-center">
              Create engaging blog posts, social media content, and marketing materials that drive results.
            </p>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Blog articles and tutorials</li>
              <li>• Social media posts</li>
              <li>• Email campaigns</li>
              <li>• Product descriptions</li>
              <li>• Marketing copy</li>
            </ul>
          </div>

          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300 transform hover:scale-105">
            <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-4 text-center">Research & Academia</h3>
            <p className="text-gray-300 mb-4 text-center">
              Generate research summaries, literature reviews, and academic content with precision.
            </p>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Literature reviews</li>
              <li>• Research summaries</li>
              <li>• Academic papers</li>
              <li>• Technical documentation</li>
              <li>• Grant proposals</li>
            </ul>
          </div>

          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300 transform hover:scale-105">
            <div className="bg-green-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Building2 className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-4 text-center">Business Intelligence</h3>
            <p className="text-gray-300 mb-4 text-center">
              Create comprehensive reports, analysis, and strategic content for decision-making.
            </p>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Market analysis</li>
              <li>• Business reports</li>
              <li>• Strategic content</li>
              <li>• Competitive analysis</li>
              <li>• Executive summaries</li>
            </ul>
          </div>

          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300 transform hover:scale-105">
            <div className="bg-orange-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-4 text-center">Technical Writing</h3>
            <p className="text-gray-300 mb-4 text-center">
              Produce clear, accurate technical documentation and instructional content.
            </p>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• API documentation</li>
              <li>• User guides</li>
              <li>• Technical tutorials</li>
              <li>• Process documentation</li>
              <li>• System specifications</li>
            </ul>
          </div>

          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300 transform hover:scale-105">
            <div className="bg-pink-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Lightbulb className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-4 text-center">Educational Content</h3>
            <p className="text-gray-300 mb-4 text-center">
              Develop engaging educational materials and training content for learners.
            </p>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Course materials</li>
              <li>• Training guides</li>
              <li>• Educational articles</li>
              <li>• Learning assessments</li>
              <li>• Curriculum development</li>
            </ul>
          </div>

          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300 transform hover:scale-105">
            <div className="bg-indigo-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Target className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-4 text-center">Creative Writing</h3>
            <p className="text-gray-300 mb-4 text-center">
              Generate creative content, stories, and engaging narratives for various purposes.
            </p>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Creative stories</li>
              <li>• Brand narratives</li>
              <li>• Content scripts</li>
              <li>• Marketing copy</li>
              <li>• Content strategies</li>
            </ul>
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Why Choose Our Solutions?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Rocket className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Fast Implementation</h3>
              <p className="text-gray-300 text-sm">Get started in minutes, not hours</p>
            </div>
            
            <div className="text-center">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Team Collaboration</h3>
              <p className="text-gray-300 text-sm">Built for teams of all sizes</p>
            </div>
            
            <div className="text-center">
              <div className="bg-gradient-to-r from-green-600 to-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">AI-Powered</h3>
              <p className="text-gray-300 text-sm">Advanced LangGraph technology</p>
            </div>
            
            <div className="text-center">
              <div className="bg-gradient-to-r from-orange-600 to-red-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Customizable</h3>
              <p className="text-gray-300 text-sm">Tailored to your specific needs</p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
          <h2 className="text-2xl sm:text-3xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Choose the solution that fits your needs and start creating exceptional content today.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signin" passHref>
              <Button
                size="lg"
                className="w-full sm:w-auto bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/pricing" passHref>
              <Button
                size="lg"
                variant="outline"
                className="w-full sm:w-auto border-purple-400 text-purple-500 hover:bg-purple-900/20 border-2 font-semibold px-8 py-3 rounded-full shadow-md transition-all duration-300 hover:scale-105"
              >
                View Pricing
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}