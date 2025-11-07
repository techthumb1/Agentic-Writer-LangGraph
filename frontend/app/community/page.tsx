// File: frontend/app/community/page.tsx
// Enhanced Community page for AI Content Studio

import { Metadata } from 'next';
import Link from 'next/link';
import { 
  Users, 
  MessageSquare, 
  Calendar, 
  Award, 
  Github, 
  BookOpen, 
  Lightbulb, 
  Heart, 
  Code, 
  Zap, 
  Globe, 
  ExternalLink,
  Twitter,
  Linkedin,
  Youtube,
  Coffee,
  Star,
  TrendingUp
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Community | AI Content Studio',
  description: 'Join our vibrant community of developers, creators, and AI enthusiasts building the future of content generation.',
};

export default function CommunityPage() {
  const communityStats = [
    {
      number: '15K+',
      label: 'Community Members',
      icon: Users
    },
    {
      number: '2.5K+',
      label: 'Discord Active Users',
      icon: MessageSquare
    },
    {
      number: '500+',
      label: 'GitHub Contributors',
      icon: Github
    },
    {
      number: '50+',
      label: 'Monthly Events',
      icon: Calendar
    }
  ];

  const platforms = [
    {
      name: 'Discord',
      description: 'Join our main community hub for real-time discussions, support, and collaboration.',
      members: '2.5K+ active members',
      icon: MessageSquare,
      color: 'from-indigo-500 to-purple-500',
      link: 'https://discord.gg/writerzroom',
      features: ['24/7 Support', 'Developer Chat', 'Live Events', 'Beta Access']
    },
    {
      name: 'GitHub',
      description: 'Contribute to our open-source projects and explore community-built tools.',
      members: '500+ contributors',
      icon: Github,
      color: 'from-gray-600 to-gray-800',
      link: 'https://github.com/writerzroom',
      features: ['Open Source', 'Code Examples', 'Issue Tracking', 'Pull Requests']
    },
    {
      name: 'Forum',
      description: 'Long-form discussions, tutorials, and knowledge sharing with the community.',
      members: '8K+ discussions',
      icon: BookOpen,
      color: 'from-green-500 to-emerald-500',
      link: 'https://forum.writerzroom.com',
      features: ['Q&A Support', 'Tutorials', 'Use Cases', 'Best Practices']
    },
    {
      name: 'Reddit',
      description: 'Casual discussions, news, and community-driven content about AI and content generation.',
      members: '12K+ subscribers',
      icon: Globe,
      color: 'from-orange-500 to-red-500',
      link: 'https://reddit.com/r/writerzroom',
      features: ['News & Updates', 'AMA Sessions', 'Community Posts', 'Memes & Fun']
    }
  ];

  const programs = [
    {
      title: 'Developer Ambassador',
      description: 'Lead community initiatives, create content, and get exclusive access to new features.',
      icon: Award,
      benefits: ['Early access to features', 'Direct line to product team', 'Speaker opportunities', 'Swag and rewards'],
      requirements: ['Active community participation', 'Technical expertise', 'Content creation'],
      color: 'from-purple-500 to-pink-500'
    },
    {
      title: 'Open Source Contributors',
      description: 'Contribute to our open-source projects and help build the future of AI content generation.',
      icon: Code,
      benefits: ['Recognition in releases', 'Contributor badges', 'Priority support', 'Networking opportunities'],
      requirements: ['GitHub account', 'Programming experience', 'Code quality standards'],
      color: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Content Creators',
      description: 'Share your AI content generation knowledge through tutorials, blogs, and videos.',
      icon: Lightbulb,
      benefits: ['Content amplification', 'Co-marketing opportunities', 'Creator fund eligibility', 'Community spotlight'],
      requirements: ['Content creation experience', 'AI/ML knowledge', 'Regular publishing schedule'],
      color: 'from-green-500 to-emerald-500'
    },
    {
      title: 'Beta Testers',
      description: 'Get early access to new features and help shape the product roadmap.',
      icon: Zap,
      benefits: ['Beta feature access', 'Product feedback sessions', 'Bug bounty eligibility', 'Special recognition'],
      requirements: ['Active platform usage', 'Detailed feedback', 'NDA compliance'],
      color: 'from-yellow-500 to-orange-500'
    }
  ];

  const events = [
    {
      title: 'AI Content Generation Workshop',
      date: '2025-01-25',
      time: '2:00 PM PST',
      type: 'Workshop',
      description: 'Hands-on workshop covering advanced LangGraph workflows and multi-agent content generation.',
      speaker: 'Dr. Emily Watson, Head of AI Research',
      platform: 'Discord + YouTube Live'
    },
    {
      title: 'Community Office Hours',
      date: '2025-01-30',
      time: '10:00 AM PST',
      type: 'Q&A Session',
      description: 'Weekly office hours with our engineering team to answer technical questions and discuss feature requests.',
      speaker: 'Marcus Rodriguez, CTO',
      platform: 'Discord Voice Chat'
    },
    {
      title: 'Developer Showcase',
      date: '2025-02-05',
      time: '3:00 PM PST',
      type: 'Showcase',
      description: 'Community members present their innovative projects and use cases built with AI Content Studio.',
      speaker: 'Community Contributors',
      platform: 'YouTube Live'
    },
    {
      title: 'AI Ethics Panel Discussion',
      date: '2025-02-15',
      time: '1:00 PM PST',
      type: 'Panel',
      description: 'Industry experts discuss responsible AI development and the future of human-AI collaboration.',
      speaker: 'Industry Panel',
      platform: 'Discord + LinkedIn Live'
    }
  ];

  const resources = [
    {
      title: 'Getting Started Guide',
      description: 'Complete beginner&apos;s guide to AI Content Studio',
      type: 'Documentation',
      link: '/docs/getting-started',
      icon: BookOpen
    },
    {
      title: 'Community Code Examples',
      description: 'Open-source examples and templates from the community',
      type: 'GitHub Repository',
      link: 'https://github.com/writerzroom/examples',
      icon: Code
    },
    {
      title: 'Video Tutorials',
      description: 'Step-by-step video guides and tutorials',
      type: 'YouTube Playlist',
      link: 'https://youtube.com/writerzroom',
      icon: Youtube
    },
    {
      title: 'API Cookbook',
      description: 'Recipes and patterns for common API use cases',
      type: 'Interactive Guide',
      link: '/docs/cookbook',
      icon: Coffee
    }
  ];

  const highlights = [
    {
      title: 'Featured Project: AI Blog Generator',
      author: '@alexchen_dev',
      description: 'Open-source tool that generates SEO-optimized blog posts using our API with custom style profiles.',
      stars: '234',
      link: 'https://github.com/community/ai-blog-generator'
    },
    {
      title: 'Tutorial: Building Multi-Agent Workflows',
      author: '@sarah_creates',
      description: 'Comprehensive guide on creating complex content generation workflows using LangGraph integration.',
      views: '15.2K',
      link: 'https://medium.com/@sarah_creates/multi-agent-workflows'
    },
    {
      title: 'Case Study: Enterprise Content Pipeline',
      author: '@enterprise_dev',
      description: 'How TechCorp automated their content pipeline and increased productivity by 300% using our platform.',
      engagement: '89% helpful',
      link: '/community/case-studies/techcorp-pipeline'
    }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Join Our Community
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Connect with developers, creators, and AI enthusiasts from around the world. Share knowledge, 
            collaborate on projects, and help shape the future of AI-powered content generation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="https://discord.gg/writerzroom" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-lg transition-all duration-300 inline-flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Join Discord
            </a>
            <Link href="#programs" className="border border-white/30 text-white hover:bg-white/10 font-semibold px-8 py-3 rounded-lg transition-all duration-300 inline-flex items-center gap-2">
              <Award className="w-4 h-4" />
              Explore Programs
            </Link>
          </div>
        </div>

        {/* Community Stats */}
        <section className="mb-16">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {communityStats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                  <stat.icon className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                  <div className="text-3xl font-bold text-white mb-2">{stat.number}</div>
                  <p className="text-gray-300">{stat.label}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Community Platforms */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Community Platforms</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {platforms.map((platform, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-r ${platform.color} rounded-lg flex items-center justify-center`}>
                    <platform.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white">{platform.name}</h3>
                    <p className="text-purple-400 text-sm">{platform.members}</p>
                  </div>
                </div>
                <p className="text-gray-300 mb-6">{platform.description}</p>
                
                <div className="grid grid-cols-2 gap-2 mb-6">
                  {platform.features.map((feature, featureIndex) => (
                    <span key={featureIndex} className="bg-white/10 text-gray-300 px-3 py-1 rounded-full text-sm text-center">
                      {feature}
                    </span>
                  ))}
                </div>
                
                <a href={platform.link} className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 rounded-lg transition-all duration-300 inline-flex items-center justify-center gap-2">
                  Join {platform.name}
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* Community Programs */}
        <section id="programs" className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Community Programs</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {programs.map((program, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-r ${program.color} rounded-lg flex items-center justify-center`}>
                    <program.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">{program.title}</h3>
                </div>
                <p className="text-gray-300 mb-6">{program.description}</p>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-white mb-2">Benefits</h4>
                    <ul className="space-y-1">
                      {program.benefits.map((benefit, benefitIndex) => (
                        <li key={benefitIndex} className="text-gray-300 text-sm flex items-start">
                          <Heart className="w-3 h-3 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-white mb-2">Requirements</h4>
                    <ul className="space-y-1">
                      {program.requirements.map((requirement, reqIndex) => (
                        <li key={reqIndex} className="text-gray-300 text-sm flex items-start">
                          <Star className="w-3 h-3 text-purple-400 mr-2 mt-0.5 flex-shrink-0" />
                          {requirement}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <button className="w-full mt-6 border border-purple-500/50 text-purple-400 hover:bg-purple-500/10 font-semibold py-3 rounded-lg transition-all duration-300">
                  Apply Now
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Upcoming Events */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Upcoming Events</h2>
          <div className="space-y-6">
            {events.map((event, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 hover:bg-white/15 transition-all duration-300">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full text-sm font-medium">
                        {event.type}
                      </span>
                      <span className="text-gray-400 text-sm flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(event.date).toLocaleDateString()} at {event.time}
                      </span>
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-2">{event.title}</h3>
                    <p className="text-gray-300 mb-2">{event.description}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>Speaker: {event.speaker}</span>
                      <span>Platform: {event.platform}</span>
                    </div>
                  </div>
                  <div className="mt-4 lg:mt-0 flex gap-3">
                    <button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-2 rounded-lg transition-all duration-300">
                      Register
                    </button>
                    <button className="border border-white/30 text-white hover:bg-white/10 font-semibold px-6 py-2 rounded-lg transition-all duration-300">
                      Add to Calendar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Community Resources */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Community Resources</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {resources.map((resource, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300">
                <resource.icon className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">{resource.title}</h3>
                <p className="text-gray-300 text-sm mb-3">{resource.description}</p>
                <span className="text-purple-400 text-xs font-medium mb-4 block">{resource.type}</span>
                <Link href={resource.link} className="w-full border border-purple-500/50 text-purple-400 hover:bg-purple-500/10 font-semibold py-2 px-4 rounded-lg transition-all duration-300 inline-flex items-center justify-center gap-2">
                  Access Resource
                  <ExternalLink className="w-3 h-3" />
                </Link>
              </div>
            ))}
          </div>
        </section>

        {/* Community Highlights */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Community Highlights</h2>
          <div className="space-y-6">
            {highlights.map((highlight, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-white mb-2">{highlight.title}</h3>
                    <p className="text-purple-400 text-sm mb-3">by {highlight.author}</p>
                    <p className="text-gray-300 mb-4">{highlight.description}</p>
                    <div className="flex items-center gap-4 text-sm">
                      {highlight.stars && (
                        <span className="text-yellow-400 flex items-center gap-1">
                          <Star className="w-3 h-3" />
                          {highlight.stars} stars
                        </span>
                      )}
                      {highlight.views && (
                        <span className="text-blue-400 flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          {highlight.views} views
                        </span>
                      )}
                      {highlight.engagement && (
                        <span className="text-green-400 flex items-center gap-1">
                          <Heart className="w-3 h-3" />
                          {highlight.engagement}
                        </span>
                      )}
                    </div>
                  </div>
                  <Link href={highlight.link} className="ml-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-2 rounded-lg transition-all duration-300 inline-flex items-center gap-2">
                    View
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Social Media */}
        <section>
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Follow Us</h2>
            <p className="text-gray-300 mb-6">
              Stay connected and get the latest updates from our community across all platforms.
            </p>
            <div className="flex justify-center gap-4">
              <a href="https://twitter.com/writerzroom" className="bg-[#1DA1F2] hover:bg-[#1A91DA] text-white p-3 rounded-lg transition-all duration-300">
                <Twitter className="w-6 h-6" />
              </a>
              <a href="https://linkedin.com/company/writerzroom" className="bg-[#0077B5] hover:bg-[#006BA6] text-white p-3 rounded-lg transition-all duration-300">
                <Linkedin className="w-6 h-6" />
              </a>
              <a href="https://youtube.com/writerzroom" className="bg-[#FF0000] hover:bg-[#E60000] text-white p-3 rounded-lg transition-all duration-300">
                <Youtube className="w-6 h-6" />
              </a>
              <a href="https://github.com/writerzroom" className="bg-gray-800 hover:bg-gray-700 text-white p-3 rounded-lg transition-all duration-300">
                <Github className="w-6 h-6" />
              </a>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
