"use client"

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { 
  ArrowRight, 
  ArrowLeft,
  TrendingUp,
  Clock,
  DollarSign,
  FileText,
  Users,
  Target,
  CheckCircle,
  Quote,
  Building2
} from 'lucide-react';

export default function ProLyficCaseStudyPage() {
  const metrics = [
    {
      icon: TrendingUp,
      label: "Content Production",
      before: "12 articles/month",
      after: "36 articles/month",
      improvement: "+250%",
      color: "text-green-400"
    },
    {
      icon: DollarSign,
      label: "Content Creation Costs",
      before: "$15,000/month",
      after: "$9,000/month",
      improvement: "-40%",
      color: "text-blue-400"
    },
    {
      icon: Clock,
      label: "Time to Market",
      before: "14 days",
      after: "7 days",
      improvement: "-50%",
      color: "text-purple-400"
    },
    {
      icon: FileText,
      label: "Content Quality Score",
      before: "7.2/10",
      after: "8.8/10",
      improvement: "+22%",
      color: "text-pink-400"
    }
  ];

  const timeline = [
    {
      phase: "Discovery & Setup",
      duration: "Week 1-2",
      activities: [
        "Content audit and strategy assessment",
        "WriterzRoom onboarding and training",
        "Custom template creation for ProLyfic's brand voice",
        "Integration with existing content workflow"
      ]
    },
    {
      phase: "Pilot Program",
      duration: "Week 3-6",
      activities: [
        "Generated 10 blog articles using AI assistance",
        "A/B tested AI vs. human-only content performance",
        "Refined style profiles and content templates",
        "Team training on advanced features"
      ]
    },
    {
      phase: "Full Deployment",
      duration: "Week 7-12",
      activities: [
        "Scaled to full content calendar (36 pieces/month)",
        "Implemented automated content workflows",
        "Integrated SEO optimization features",
        "Established content performance tracking"
      ]
    }
  ];

  const results = [
    {
      metric: "250% Increase in Content Volume",
      description: "From 12 to 36 high-quality articles per month, enabling ProLyfic to dominate their content marketing space."
    },
    {
      metric: "40% Reduction in Content Costs",
      description: "Reduced monthly content creation budget from $15,000 to $9,000 while improving quality and volume."
    },
    {
      metric: "50% Faster Time-to-Market",
      description: "Cut content production cycle from 14 days to 7 days, enabling rapid response to market opportunities."
    },
    {
      metric: "22% Improvement in Quality Scores",
      description: "Enhanced content quality from 7.2/10 to 8.8/10 based on engagement metrics and editorial reviews."
    }
  ];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto text-white">
        {/* Back Navigation */}
        <div className="mb-8">
          <Link href="/customers" className="inline-flex items-center text-purple-400 hover:text-purple-300 transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Customers
          </Link>
        </div>

        {/* Header */}
        <header className="text-center mb-16">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 mb-8">
            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              ProLyfic Solutions
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                {" "}Success Story
              </span>
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed max-w-3xl mx-auto mb-6">
              How a growing SaaS company tripled their content output while reducing costs by 40% 
              using WriterzRoom&apos;s AI-powered content generation platform.
            </p>
            <div className="flex items-center justify-center space-x-8 text-sm text-gray-400">
              <div className="flex items-center">
                <Building2 className="h-4 w-4 mr-2" />
                SaaS Technology
              </div>
              <div className="flex items-center">
                <Users className="h-4 w-4 mr-2" />
                150+ Employees
              </div>
              <div className="flex items-center">
                <Target className="h-4 w-4 mr-2" />
                B2B Marketing
              </div>
            </div>
          </div>
        </header>

        {/* Challenge Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">The Challenge</h2>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold mb-4 text-purple-400">Growing Demand, Limited Resources</h3>
                <p className="text-gray-300 mb-4">
                  ProLyfic Solutions was experiencing rapid growth but struggling to keep up with content demands. 
                  Their marketing team of 3 people was only producing 12 articles per month, far below what was 
                  needed to support their expanding product line and customer base.
                </p>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    Content production bottleneck limiting growth
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    High costs of hiring additional writers
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    Inconsistent brand voice across content
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    Long lead times for content campaigns
                  </li>
                </ul>
              </div>
              <div className="bg-gradient-to-br from-red-600/10 to-orange-600/10 rounded-lg p-6 border border-red-400/20">
                <Quote className="h-8 w-8 text-red-400 mb-4" />
                <blockquote className="text-gray-300 italic">
                  &ldquo;We were turning down marketing opportunities because we simply couldn&apos;t produce 
                  content fast enough. Our team was burnt out, and quality was starting to suffer.&rdquo;
                </blockquote>
                <cite className="text-sm text-gray-400 mt-4 block">
                  — Maggie Kaufman, Content Marketing Manager
                </cite>
              </div>
            </div>
          </div>
        </section>

        {/* Solution Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">The Solution</h2>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-semibold mb-4 text-purple-400">WriterzRoom Implementation</h3>
              <p className="text-gray-300 max-w-3xl mx-auto">
                ProLyfic Solutions partnered with WriterzRoom to implement an AI-powered content generation 
                system that would scale with their growth while maintaining quality and brand consistency.
              </p>
            </div>
            
            <div className="space-y-8">
              {timeline.map((phase, index) => (
                <div key={index} className="border-l-2 border-purple-400 pl-6 relative">
                  <div className="absolute -left-2 top-0 w-4 h-4 bg-purple-400 rounded-full"></div>
                  <h4 className="text-lg font-semibold text-white mb-2">{phase.phase}</h4>
                  <p className="text-sm text-purple-300 mb-3">{phase.duration}</p>
                  <ul className="space-y-1">
                    {phase.activities.map((activity, actIndex) => (
                      <li key={actIndex} className="text-gray-300 text-sm flex items-start">
                        <CheckCircle className="h-4 w-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                        {activity}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Results Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">The Results</h2>
          
          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {metrics.map((metric, index) => {
              const IconComponent = metric.icon;
              return (
                <div key={index} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 text-center">
                  <IconComponent className={`h-8 w-8 mx-auto mb-4 ${metric.color}`} />
                  <h4 className="text-sm font-medium text-gray-400 mb-2">{metric.label}</h4>
                  <div className="text-xs text-gray-500 mb-1">Before: {metric.before}</div>
                  <div className="text-xs text-gray-300 mb-2">After: {metric.after}</div>
                  <div className={`text-lg font-bold ${metric.color}`}>{metric.improvement}</div>
                </div>
              );
            })}
          </div>

          {/* Detailed Results */}
          <div className="space-y-6">
            {results.map((result, index) => (
              <div key={index} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h4 className="text-xl font-semibold text-purple-400 mb-3">{result.metric}</h4>
                <p className="text-gray-300">{result.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Testimonial */}
        <section className="mb-16">
          <div className="bg-gradient-to-br from-purple-600/10 to-pink-600/10 rounded-xl p-8 border border-purple-400/20 text-center">
            <Quote className="h-12 w-12 text-purple-400 mx-auto mb-6" />
            <blockquote className="text-xl text-gray-300 italic mb-6 leading-relaxed">
              &ldquo;WriterzRoom has been transformational for our content strategy. We&apos;re not just producing 
              more content—we&apos;re producing better content, faster, and at a fraction of the cost. It&apos;s 
              allowed us to compete with much larger companies in terms of content marketing reach.&rdquo;
            </blockquote>
            <cite className="text-gray-400">
              <div className="font-semibold text-white">Maggie Kaufman</div>
              <div>Content Marketing Manager, ProLyfic Solutions</div>
            </cite>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
          <h2 className="text-2xl sm:text-3xl font-bold mb-4">
            Ready to Achieve Similar Results?
          </h2>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Join ProLyfic Solutions and thousands of other companies transforming their content creation 
            with WriterzRoom.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signin" passHref>
              <Button
                size="lg"
                className="w-full sm:w-auto bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                Start Your Success Story
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/contact" passHref>
              <Button
                size="lg"
                variant="outline"
                className="w-full sm:w-auto border-purple-400 text-purple-300 hover:bg-purple-900/20 border-2 font-semibold px-8 py-3 rounded-full shadow-md transition-all duration-300 hover:scale-105"
              >
                Schedule Demo
              </Button>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}