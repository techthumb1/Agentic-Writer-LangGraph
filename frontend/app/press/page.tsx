// File: frontend/app/press/page.tsx
// Enhanced Press page for AI Content Studio

import { Metadata } from 'next';
import Link from 'next/link';
import { 
  Download, 
  Calendar, 
  ExternalLink, 
  Award, 
  Newspaper, 
  Camera, 
  FileText, 
  Mail, 
  Users, 
  Building,
  Globe
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Press | AI Content Studio',
  description: 'Latest news, press releases, and media resources for AI Content Studio.',
};

export default function PressPage() {
  const pressReleases = [
    {
      date: '2025-01-10',
      title: 'AI Content Studio Raises $50M Series B to Accelerate Enterprise AI Adoption',
      summary: 'Funding round led by Andreessen Horowitz will fuel expansion of enterprise features and global market presence.',
      link: '/press/series-b-funding-announcement'
    },
    {
      date: '2024-12-15',
      title: 'AI Content Studio Launches Revolutionary LangGraph 2.0 Integration',
      summary: 'New multi-agent workflow capabilities enable unprecedented content generation sophistication for enterprise customers.',
      link: '/press/langgraph-2-launch'
    },
    {
      date: '2024-11-20',
      title: 'Fortune 500 Adoption Surges as AI Content Studio Achieves SOC 2 Type II Certification',
      summary: 'Compliance milestone opens doors to enterprise customers with strict security and governance requirements.',
      link: '/press/soc2-certification'
    },
    {
      date: '2024-10-05',
      title: 'AI Content Studio Partners with Microsoft to Bring AI Content Generation to Office 365',
      summary: 'Strategic partnership integrates advanced content generation capabilities directly into Microsoft&apos;s productivity suite.',
      link: '/press/microsoft-partnership'
    }
  ];

  const coverage = [
    {
      outlet: 'TechCrunch',
      title: 'AI Content Studio is revolutionizing how enterprises approach content creation',
      date: '2025-01-08',
      type: 'Feature Article',
      link: 'https://techcrunch.com/ai-content-studio-enterprise'
    },
    {
      outlet: 'The Information',
      title: 'Inside the $50M bet on AI content generation&apos;s enterprise future',
      date: '2025-01-07',
      type: 'Analysis',
      link: 'https://theinformation.com/ai-content-studio-funding'
    },
    {
      outlet: 'Forbes',
      title: 'How AI Content Studio is democratizing enterprise content creation',
      date: '2024-12-20',
      type: 'Profile',
      link: 'https://forbes.com/ai-content-studio-profile'
    },
    {
      outlet: 'VentureBeat',
      title: 'LangGraph integration puts AI Content Studio ahead in multi-agent race',
      date: '2024-12-16',
      type: 'Technical Review',
      link: 'https://venturebeat.com/ai-content-studio-langgraph'
    },
    {
      outlet: 'Wired',
      title: 'The future of content creation is collaborative AI, not replacement',
      date: '2024-11-25',
      type: 'Industry Analysis',
      link: 'https://wired.com/ai-content-collaborative-future'
    }
  ];

  const awards = [
    {
      award: 'Best AI Innovation',
      organization: 'AI Excellence Awards 2024',
      date: '2024-12-01',
      description: 'Recognized for breakthrough multi-agent content generation technology'
    },
    {
      award: 'Enterprise Software of the Year',
      organization: 'SaaS Awards 2024',
      date: '2024-11-15',
      description: 'Honored for exceptional enterprise AI platform innovation'
    },
    {
      award: 'Top 50 AI Companies',
      organization: 'Forbes AI 50',
      date: '2024-10-30',
      description: 'Named among the most promising AI companies transforming industries'
    },
    {
      award: 'Startup of the Year - AI Category',
      organization: 'TechCrunch Disrupt',
      date: '2024-09-20',
      description: 'Awarded for revolutionary approach to AI-powered content generation'
    }
  ];

  const mediaKit = [
    {
      title: 'Company Logos',
      description: 'High-resolution logos in various formats (PNG, SVG, EPS)',
      files: ['Logo Package (ZIP)', 'Brand Guidelines (PDF)'],
      icon: Camera
    },
    {
      title: 'Executive Photos',
      description: 'Professional headshots of leadership team',
      files: ['Leadership Photos (ZIP)', 'Company Photos (ZIP)'],
      icon: Users
    },
    {
      title: 'Product Screenshots',
      description: 'High-quality screenshots of platform interface',
      files: ['Dashboard Screenshots (ZIP)', 'API Documentation (ZIP)'],
      icon: FileText
    },
    {
      title: 'Company Fact Sheet',
      description: 'Key statistics, timeline, and company information',
      files: ['Fact Sheet (PDF)', 'Executive Bios (PDF)'],
      icon: Building
    }
  ];

  const keyStats = [
    { label: 'Founded', value: '2023' },
    { label: 'Headquarters', value: 'San Francisco, CA' },
    { label: 'Employees', value: '50+' },
    { label: 'Funding Raised', value: '$75M' },
    { label: 'Enterprise Customers', value: '150+' },
    { label: 'Content Generated', value: '500K+' },
    { label: 'Global Offices', value: '4' },
    { label: 'Uptime SLA', value: '99.9%' }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Press & Media
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Stay updated with the latest news, announcements, and media coverage about AI Content Studio. 
            Download our media kit and access resources for journalists and content creators.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-lg transition-all duration-300 inline-flex items-center gap-2">
              <Download className="w-4 h-4" />
              Download Media Kit
            </button>
            <Link href="/contact" className="border border-white/30 text-white hover:bg-white/10 font-semibold px-8 py-3 rounded-lg transition-all duration-300 inline-flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Media Inquiries
            </Link>
          </div>
        </div>

        {/* Key Stats */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Company at a Glance</h2>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <div className="grid md:grid-cols-4 gap-6">
              {keyStats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-purple-400 mb-1">{stat.value}</div>
                  <p className="text-gray-300 text-sm">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Latest Press Releases */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Latest Press Releases</h2>
          <div className="space-y-6">
            {pressReleases.map((release, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 hover:bg-white/15 transition-all duration-300">
                <div className="flex flex-col lg:flex-row lg:items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2">
                        <Calendar className="w-3 h-3" />
                        {new Date(release.date).toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </span>
                    </div>
                    <h3 className="text-2xl font-semibold text-white mb-3">{release.title}</h3>
                    <p className="text-gray-300 mb-4">{release.summary}</p>
                  </div>
                  <Link href={release.link} className="mt-4 lg:mt-0 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-2 rounded-lg transition-all duration-300 inline-flex items-center gap-2">
                    Read More
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Media Coverage */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Recent Media Coverage</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {coverage.map((article, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-start justify-between mb-3">
                  <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-sm font-medium">
                    {article.type}
                  </span>
                  <span className="text-gray-400 text-sm">
                    {new Date(article.date).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{article.outlet}</h3>
                <p className="text-gray-300 mb-4">&quot;{article.title}&quot;</p>
                <a href={article.link} className="text-purple-400 hover:text-purple-300 font-medium inline-flex items-center gap-2" target="_blank" rel="noopener noreferrer">
                  Read Article
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* Awards & Recognition */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Awards & Recognition</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {awards.map((award, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-start gap-4">
                  <Award className="w-8 h-8 text-yellow-400 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">{award.award}</h3>
                    <p className="text-purple-400 mb-2">{award.organization}</p>
                    <p className="text-gray-300 text-sm mb-2">{award.description}</p>
                    <span className="text-gray-400 text-sm">
                      {new Date(award.date).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long' 
                      })}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Media Kit */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Media Kit</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {mediaKit.map((kit, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300">
                <kit.icon className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-3">{kit.title}</h3>
                <p className="text-gray-300 text-sm mb-4">{kit.description}</p>
                <div className="space-y-2">
                  {kit.files.map((file, fileIndex) => (
                    <button key={fileIndex} className="w-full text-purple-400 hover:text-purple-300 text-sm font-medium py-2 px-3 rounded border border-purple-500/30 hover:bg-purple-500/10 transition-all duration-300 inline-flex items-center justify-center gap-2">
                      <Download className="w-3 h-3" />
                      {file}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Media Contact */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h2 className="text-2xl font-bold text-white mb-4">Media Contact</h2>
                <div className="space-y-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">Sarah Johnson</h3>
                    <p className="text-purple-400">Director of Communications</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-gray-300">
                      <Mail className="w-4 h-4" />
                      <a href="mailto:press@aicontentstudio.com" className="hover:text-purple-400 transition-colors">
                        press@aicontentstudio.com
                      </a>
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <Globe className="w-4 h-4" />
                      <span>Available for interviews worldwide</span>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-4">Quick Facts</h2>
                <div className="space-y-2 text-gray-300">
                  <p>• Leading AI content generation platform</p>
                  <p>• Serving 150+ enterprise customers</p>
                  <p>• $75M in total funding raised</p>
                  <p>• SOC 2 Type II certified</p>
                  <p>• 99.9% uptime SLA</p>
                  <p>• Founded by former Meta and Google AI leaders</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Newsletter Signup */}
        <section>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 text-center">
            <Newspaper className="w-16 h-16 text-purple-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-4">Stay Updated</h2>
            <p className="text-gray-300 mb-6">
              Subscribe to our press newsletter to receive the latest company news and announcements.
            </p>
            <div className="max-w-md mx-auto flex gap-4">
              <input 
                type="email" 
                placeholder="Enter your email" 
                className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300">
                Subscribe
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}