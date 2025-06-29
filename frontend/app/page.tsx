// File: frontend/app/page.tsx
'use client';

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowRight, Sparkles, Zap, Target, Users, Shield, Rocket } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-6 py-12">
        <section className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] text-center">
          {/* Hero Header */}
          <header className="max-w-4xl space-y-6">
            <div className="flex justify-center mb-6">
              <div className="flex items-center space-x-2 bg-primary/10 backdrop-blur-sm border border-primary/20 rounded-full px-4 py-2">
                <Sparkles className="h-5 w-5 text-primary" />
                <span className="text-sm text-primary">AI-Powered Content Generation Platform</span>
              </div>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 leading-tight text-foreground">
              Transform Your Ideas Into{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                Outstanding Content
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl mb-12 leading-relaxed text-muted-foreground max-w-3xl mx-auto">
              Generate high-quality, customized content across various formats and styles, tailored to your specific needs.
              From technical articles to research summaries, let our advanced AI agents handle the heavy lifting while you focus on what matters most.
            </p>
          </header>

          {/* CTA Buttons */}
          <div className="flex flex-wrap justify-center gap-4 mb-16">
            <Link href="/auth/signin" passHref>
              <Button
                size="lg"
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="#features" passHref>
              <Button
                size="lg"
                variant="outline"
                className="border-primary text-primary hover:bg-primary/10 border-2 font-semibold px-8 py-3 rounded-full shadow-md transition-all duration-300 hover:scale-105"
              >
                Learn More
              </Button>
            </Link>
          </div>

          {/* Feature Cards */}
          <div id="features" className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full mb-10">
            <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6 text-center hover:bg-card/70 transition-all duration-300">
              <div className="bg-primary w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Zap className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">Lightning Fast</h3>
              <p className="text-muted-foreground text-sm">Generate high-quality content in seconds, not hours. Our AI processes your requirements instantly.</p>
            </div>
            
            <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6 text-center hover:bg-card/70 transition-all duration-300">
              <div className="bg-gradient-to-r from-pink-500 to-purple-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Target className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">Highly Targeted</h3>
              <p className="text-muted-foreground text-sm">Content perfectly matched to your style, audience, and specific requirements with customizable templates.</p>
            </div>
            
            <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6 text-center hover:bg-card/70 transition-all duration-300">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">AI-Enhanced</h3>
              <p className="text-muted-foreground text-sm">Powered by cutting-edge LangGraph and multi-agent AI technology for superior, contextual results.</p>
            </div>
          </div>

          {/* Additional Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full mb-16">
            <div className="flex flex-col items-center text-center space-y-2 text-muted-foreground">
              <Users className="h-5 w-5 text-primary" />
              <span>Multi-agent collaboration</span>
            </div>
            <div className="flex flex-col items-center text-center space-y-2 text-muted-foreground">
              <Shield className="h-5 w-5 text-primary" />
              <span>Secure & private</span>
            </div>
            <div className="flex flex-col items-center text-center space-y-2 text-muted-foreground">
              <Rocket className="h-5 w-5 text-primary" />
              <span>Enterprise ready</span>
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-8 text-muted-foreground text-sm max-w-2xl">
            <p>
              Join thousands of content creators, researchers, and businesses who trust our AI platform 
              to generate exceptional content that drives results.
            </p>
          </footer>
        </section>
      </div>
    </div>
  );
}