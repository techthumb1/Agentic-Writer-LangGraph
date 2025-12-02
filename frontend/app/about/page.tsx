// File: frontend/app/about/page.tsx
// Enhanced About Us page for AI Content Studio

import { Metadata } from 'next';
import Link from 'next/link';
import { 
  Users, 
  Target, 
  Award, 
  Globe, 
  Brain, 
  Shield, 
  Heart, 
  TrendingUp, 
  Building, 
  Calendar, 
  MapPin,
  Linkedin,
  Twitter,
  Github
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'About Us | AI Content Studio',
  description: 'Learn about our mission to democratize AI content generation and empower creators worldwide.',
};

export default function AboutPage() {
  const stats = [
    {
      number: '500K+',
      label: 'Content Pieces Generated',
      icon: Brain
    },
    {
      number: '10K+',
      label: 'Active Users',
      icon: Users
    },
    {
      number: '150+',
      label: 'Enterprise Customers',
      icon: Building
    },
    {
      number: '99.9%',
      label: 'Uptime SLA',
      icon: Shield
    }
  ];

  const values = [
    {
      title: 'Innovation First',
      description: 'We push the boundaries of what&apos;s possible with AI, constantly exploring new frontiers in content generation and multi-agent orchestration.',
      icon: Brain
    },
    {
      title: 'User-Centric Design',
      description: 'Every feature we build starts with understanding our users&apos; needs. We create tools that augment human creativity rather than replace it.',
      icon: Heart
    },
    {
      title: 'Enterprise Security',
      description: 'Security and compliance are built into our DNA. We maintain the highest standards to protect our customers&apos; data and content.',
      icon: Shield
    },
    {
      title: 'Open Collaboration',
      description: 'We believe in the power of community and open-source development. We contribute back and learn from the global AI community.',
      icon: Globe
    },
    {
      title: 'Ethical AI',
      description: 'We are committed to developing AI responsibly, ensuring our technology benefits society and respects user privacy and rights.',
      icon: Award
    },
    {
      title: 'Continuous Growth',
      description: 'We foster a culture of learning and adaptation, staying ahead of the rapidly evolving AI landscape through continuous innovation.',
      icon: TrendingUp
    }
  ];

  const timeline = [
    {
      year: '2023',
      title: 'Company Founded',
      description: 'AI Content Studio was founded with a vision to democratize AI-powered content creation for businesses and creators worldwide.'
    },
    {
      year: '2023',
      title: 'First Product Launch',
      description: 'Launched our initial content generation platform with support for basic templates and style profiles.'
    },
    {
      year: '2024',
      title: 'LangGraph Integration',
      description: 'Introduced revolutionary multi-agent workflows with LangGraph, enabling complex content generation orchestration.'
    },
    {
      year: '2024',
      title: 'Enterprise Expansion',
      description: 'Launched enterprise features including SSO, audit logging, and custom deployment options for Fortune 500 companies.'
    },
    {
      year: '2024',
      title: 'Global Presence',
      description: 'Opened offices in New York, Austin, and London to support our growing international customer base.'
    },
    {
      year: '2025',
      title: 'AI Innovation Lab',
      description: 'Established our AI Innovation Lab focusing on next-generation content generation and federated learning research.'
    }
  ];

  const team = [
    {
      name: 'Sarah Chen',
      role: 'CEO & Co-Founder',
      bio: 'Former VP of AI at Meta, leading expert in large language models and content generation. PhD in Computer Science from Stanford.',
      image: '/team/sarah-chen.jpg',
      linkedin: 'https://linkedin.com/in/sarahchen',
      twitter: 'https://twitter.com/sarahchen'
    },
    {
      name: 'Marcus Rodriguez',
      role: 'CTO & Co-Founder',
      bio: 'Previously Senior Principal Engineer at Google AI. Specialist in distributed systems and ML infrastructure. MS from MIT.',
      image: '/team/marcus-rodriguez.jpg',
      linkedin: 'https://linkedin.com/in/marcusrodriguez',
      github: 'https://github.com/marcusrodriguez'
    },
    {
      name: 'Dr. Emily Watson',
      role: 'Head of AI Research',
      bio: 'Former Research Scientist at OpenAI. Leading researcher in multi-agent systems and content generation. PhD from Berkeley.',
      image: '/team/emily-watson.jpg',
      linkedin: 'https://linkedin.com/in/emilywatson',
      twitter: 'https://twitter.com/emilywatson'
    },
    {
      name: 'David Kim',
      role: 'VP of Engineering',
      bio: 'Previously Engineering Manager at Stripe. Expert in scalable platform architecture and developer tools. BS from Carnegie Mellon.',
      image: '/team/david-kim.jpg',
      linkedin: 'https://linkedin.com/in/davidkim',
      github: 'https://github.com/davidkim'
    }
  ];

  const investors = [
    { name: 'Andreessen Horowitz', logo: '/investors/a16z.png' },
    { name: 'Sequoia Capital', logo: '/investors/sequoia.png' },
    { name: 'GV (Google Ventures)', logo: '/investors/gv.png' },
    { name: 'Kleiner Perkins', logo: '/investors/kp.png' }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            About AI Content Studio
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            We&apos;re on a mission to democratize AI-powered content creation, empowering businesses and creators 
            to produce high-quality content at scale while maintaining their unique voice and style.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-400">
            <span className="bg-white/10 px-4 py-2 rounded-full flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Founded 2023
            </span>
            <span className="bg-white/10 px-4 py-2 rounded-full flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              San Francisco, CA
            </span>
            <span className="bg-white/10 px-4 py-2 rounded-full flex items-center gap-2">
              <Users className="w-4 h-4" />
              50+ Team Members
            </span>
          </div>
        </div>

        {/* Stats Section */}
        <section className="mb-16">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
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

        {/* Mission Statement */}
        <section className="mb-16">
          <div className="bg-linear-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <div className="text-center mb-8">
              <Target className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-white mb-4">Our Mission</h2>
            </div>
            <p className="text-lg text-gray-300 text-center max-w-4xl mx-auto leading-relaxed">
              To empower every creator, business, and organization with AI-powered content generation tools that enhance 
              human creativity rather than replace it. We believe in a future where AI serves as a collaborative partner, 
              helping people express their ideas more effectively and reach their audiences with compelling, authentic content.
            </p>
          </div>
        </section>

        {/* Values */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Our Values</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {values.map((value, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                <value.icon className="w-8 h-8 text-purple-400 mb-4" />
                <h3 className="text-xl font-semibold text-white mb-3">{value.title}</h3>
                <p className="text-gray-300">{value.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Timeline */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Our Journey</h2>
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-linear-to-b from-purple-500 to-pink-500"></div>
            
            <div className="space-y-8">
              {timeline.map((item, index) => (
                <div key={index} className="relative flex items-start">
                  {/* Timeline dot */}
                  <div className="absolute left-2 w-4 h-4 bg-linear-to-r from-purple-500 to-pink-500 rounded-full border-2 border-gray-900"></div>
                  
                  {/* Content */}
                  <div className="ml-12 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <span className="bg-linear-to-r from-purple-500 to-pink-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                        {item.year}
                      </span>
                      <h3 className="text-xl font-semibold text-white">{item.title}</h3>
                    </div>
                    <p className="text-gray-300">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Team */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Leadership Team</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {team.map((member, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300">
                <div className="w-24 h-24 bg-linear-to-r from-purple-500 to-pink-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <Users className="w-12 h-12 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-1">{member.name}</h3>
                <p className="text-purple-400 text-sm mb-3">{member.role}</p>
                <p className="text-gray-300 text-sm mb-4">{member.bio}</p>
                
                <div className="flex justify-center gap-3">
                  {member.linkedin && (
                    <a href={member.linkedin} className="text-gray-400 hover:text-purple-400 transition-colors">
                      <Linkedin className="w-4 h-4" />
                    </a>
                  )}
                  {member.twitter && (
                    <a href={member.twitter} className="text-gray-400 hover:text-purple-400 transition-colors">
                      <Twitter className="w-4 h-4" />
                    </a>
                  )}
                  {member.github && (
                    <a href={member.github} className="text-gray-400 hover:text-purple-400 transition-colors">
                      <Github className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Investors */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Backed by Leading Investors</h2>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 items-center">
              {investors.map((investor, index) => (
                <div key={index} className="text-center">
                  <div className="bg-white/20 rounded-lg p-6 mb-4">
                    <div className="h-12 flex items-center justify-center">
                      <span className="text-white font-semibold">{investor.name}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center">
          <div className="bg-linear-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-3xl font-bold text-white mb-4">Join Our Mission</h2>
            <p className="text-xl text-gray-300 mb-6">
              Ready to be part of the future of AI-powered content creation?
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/careers" className="bg-linear-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-lg transition-all duration-300">
                View Open Positions
              </Link>
              <Link href="/contact" className="border border-white/30 text-white hover:bg-white/10 font-semibold px-8 py-3 rounded-lg transition-all duration-300">
                Get in Touch
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}