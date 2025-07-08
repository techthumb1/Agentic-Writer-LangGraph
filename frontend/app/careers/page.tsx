// File: frontend/app/careers/page.tsx
// Enhanced Careers page for AI Content Studio (Professional - No Emojis)

import { Metadata } from 'next';
import Link from 'next/link';
import { 
  Heart, 
  Globe, 
  BookOpen, 
  Rocket, 
  Umbrella, 
  MapPin, 
  Building, 
  DollarSign, 
  CheckCircle, 
  Circle
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Careers | AI Content Studio',
  description: 'Join our team and help shape the future of AI content generation with cutting-edge LangGraph orchestration and multi-modal AI systems.',
};

export default function CareersPage() {
  const openPositions = [
    {
      id: 1,
      title: 'Senior Machine Learning Engineer',
      department: 'Engineering',
      location: 'Remote / San Francisco',
      type: 'Full-time',
      salary: '$180k - $250k',
      description: 'Lead development of our next-generation AI content models and LangGraph orchestration systems. Work on cutting-edge multi-agent workflows and content generation pipelines.',
      requirements: [
        '5+ years in ML/AI engineering with production experience',
        'Experience with LLMs, transformers, and content generation',
        'Python, PyTorch/TensorFlow, LangChain/LangGraph expertise',
        'Knowledge of distributed systems and model deployment',
        'Experience with agent-based systems and workflow orchestration'
      ],
      responsibilities: [
        'Design and implement AI agent workflows using LangGraph',
        'Optimize content generation models for performance and quality',
        'Build scalable ML infrastructure and deployment pipelines',
        'Collaborate on research initiatives and model improvements'
      ]
    },
    {
      id: 2,
      title: 'AI Research Scientist',
      department: 'Research',
      location: 'Remote / New York',
      type: 'Full-time',
      salary: '$200k - $300k',
      description: 'Research and develop cutting-edge AI techniques for multi-modal content generation, focusing on novel approaches to agent coordination and content optimization.',
      requirements: [
        'PhD in Computer Science, AI, or related field',
        'Published research in NLP, computer vision, or generative AI',
        'Experience with reinforcement learning and multi-agent systems',
        'Strong mathematical and statistical background',
        'Knowledge of federated learning and distributed AI systems'
      ],
      responsibilities: [
        'Conduct research on advanced content generation techniques',
        'Develop novel multi-agent coordination strategies',
        'Publish findings in top-tier conferences and journals',
        'Mentor junior researchers and engineers'
      ]
    },
    {
      id: 3,
      title: 'Full Stack Developer (AI Platform)',
      department: 'Engineering',
      location: 'Remote',
      type: 'Full-time',
      salary: '$140k - $180k',
      description: 'Build and enhance our Next.js platform with modern web technologies, integrating complex AI workflows and real-time content generation features.',
      requirements: [
        '4+ years in full-stack development',
        'Next.js, React, TypeScript, Node.js expertise',
        'Experience with Prisma, PostgreSQL, and real-time systems',
        'Understanding of AI/ML integration in web applications',
        'Knowledge of WebSocket, streaming, and async processing'
      ],
      responsibilities: [
        'Develop responsive web interfaces for AI content generation',
        'Integrate LangGraph workflows with frontend applications',
        'Build real-time collaboration features and live updates',
        'Optimize performance for complex AI-driven workflows'
      ]
    },
    {
      id: 4,
      title: 'DevOps Engineer (AI Infrastructure)',
      department: 'Infrastructure',
      location: 'Remote / Austin',
      type: 'Full-time',
      salary: '$150k - $200k',
      description: 'Design and maintain infrastructure for large-scale AI content generation, managing GPU clusters, model serving, and distributed computing systems.',
      requirements: [
        '5+ years in DevOps/Infrastructure engineering',
        'Experience with Kubernetes, Docker, and cloud platforms',
        'Knowledge of GPU orchestration and ML model serving',
        'Familiarity with monitoring, logging, and observability',
        'Understanding of AI/ML infrastructure requirements'
      ],
      responsibilities: [
        'Manage GPU clusters and model serving infrastructure',
        'Implement CI/CD pipelines for ML model deployment',
        'Monitor and optimize system performance and costs',
        'Ensure high availability and disaster recovery'
      ]
    },
    {
      id: 5,
      title: 'Product Manager (AI Features)',
      department: 'Product',
      location: 'Remote / Seattle',
      type: 'Full-time',
      salary: '$160k - $220k',
      description: 'Drive product strategy for AI-powered content generation features, working closely with engineering and research teams to deliver innovative solutions.',
      requirements: [
        '5+ years in product management, preferably AI/ML products',
        'Experience with enterprise software and content tools',
        'Strong analytical and user research skills',
        'Understanding of AI capabilities and limitations',
        'Track record of successful product launches'
      ],
      responsibilities: [
        'Define product roadmap for AI content generation features',
        'Collaborate with customers to understand requirements',
        'Work with engineering teams on feature specifications',
        'Analyze product metrics and user feedback'
      ]
    }
  ];

  const benefits = [
    {
      icon: Heart,
      title: 'Health & Wellness',
      description: 'Comprehensive health, dental, and vision insurance. Mental health support and wellness stipend.'
    },
    {
      icon: DollarSign,
      title: 'Competitive Compensation',
      description: 'Top-tier salaries, equity options, and performance bonuses. Annual compensation reviews.'
    },
    {
      icon: Globe,
      title: 'Remote-First Culture',
      description: 'Work from anywhere with flexible hours. Home office setup stipend and co-working allowances.'
    },
    {
      icon: BookOpen,
      title: 'Learning & Development',
      description: 'Conference attendance, online courses, and research time. AI/ML certification support.'
    },
    {
      icon: Rocket,
      title: 'Innovation Time',
      description: '20% time for personal projects and research. Access to latest AI tools and technologies.'
    },
    {
      icon: Umbrella,
      title: 'Time Off',
      description: 'Unlimited PTO policy with minimum 3 weeks encouraged. Sabbatical opportunities.'
    }
  ];

  const values = [
    {
      title: 'AI for Good',
      description: 'We believe AI should augment human creativity, not replace it. Our tools empower creators and knowledge workers.'
    },
    {
      title: 'Open Innovation',
      description: 'We contribute to open-source projects and share research findings with the broader AI community.'
    },
    {
      title: 'Diverse Perspectives',
      description: 'Our team includes diverse backgrounds in AI, content creation, design, and domain expertise.'
    },
    {
      title: 'Continuous Learning',
      description: 'The AI field evolves rapidly. We encourage experimentation, learning from failures, and knowledge sharing.'
    }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Join the Future of AI Content Generation
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Help us build the next generation of AI-powered content tools. Work with cutting-edge LangGraph orchestration, 
            multi-agent systems, and enterprise-scale content generation platforms.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-400">
            <span className="bg-white/10 px-4 py-2 rounded-full">Remote-First</span>
            <span className="bg-white/10 px-4 py-2 rounded-full">AI Research</span>
            <span className="bg-white/10 px-4 py-2 rounded-full">LangGraph</span>
            <span className="bg-white/10 px-4 py-2 rounded-full">Enterprise Scale</span>
          </div>
        </div>

        {/* Open Positions */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Open Positions</h2>
          <div className="space-y-6">
            {openPositions.map((position) => (
              <div key={position.id} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 hover:bg-white/15 transition-all duration-300">
                <div className="flex flex-col lg:flex-row lg:items-start justify-between mb-6">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <h3 className="text-2xl font-semibold text-white">{position.title}</h3>
                      <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                        {position.type}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-4 text-gray-300 mb-4">
                      <span className="flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        {position.location}
                      </span>
                      <span className="flex items-center gap-2">
                        <Building className="w-4 h-4" />
                        {position.department}
                      </span>
                      <span className="flex items-center gap-2">
                        <DollarSign className="w-4 h-4" />
                        {position.salary}
                      </span>
                    </div>
                    <p className="text-gray-300 mb-6">{position.description}</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">Requirements</h4>
                    <ul className="space-y-2">
                      {position.requirements.map((req, index) => (
                        <li key={index} className="text-gray-300 flex items-start">
                          <CheckCircle className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                          {req}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">Key Responsibilities</h4>
                    <ul className="space-y-2">
                      {position.responsibilities.map((resp, index) => (
                        <li key={index} className="text-gray-300 flex items-start">
                          <Circle className="w-4 h-4 text-blue-400 mr-2 mt-0.5 flex-shrink-0" />
                          {resp}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-white/20">
                  <button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300 mr-4">
                    Apply Now
                  </button>
                  <button className="border border-white/30 text-white hover:bg-white/10 font-semibold px-6 py-3 rounded-lg transition-all duration-300">
                    Learn More
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Benefits */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Why Join Us?</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((benefit, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300">
                <benefit.icon className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-3">{benefit.title}</h3>
                <p className="text-gray-300">{benefit.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Company Values */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Our Values</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {values.map((value, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                <h3 className="text-xl font-semibold text-white mb-3">{value.title}</h3>
                <p className="text-gray-300">{value.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Application Process */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Application Process</h2>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <div className="grid md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">1</div>
                <h3 className="text-lg font-semibold text-white mb-2">Application</h3>
                <p className="text-gray-300">Submit your resume and cover letter</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">2</div>
                <h3 className="text-lg font-semibold text-white mb-2">Screening</h3>
                <p className="text-gray-300">Initial phone/video screening</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">3</div>
                <h3 className="text-lg font-semibold text-white mb-2">Technical</h3>
                <p className="text-gray-300">Technical interview and/or assignment</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">4</div>
                <h3 className="text-lg font-semibold text-white mb-2">Final Round</h3>
                <p className="text-gray-300">Team interviews and culture fit</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Shape the Future?</h2>
          <p className="text-xl text-gray-300 mb-6">
            Don&apos;t see a position that fits? We&apos;re always looking for exceptional talent.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-lg transition-all duration-300">
              Send Us Your Resume
            </button>
            <Link 
              href="/contact"
              className="border border-white/30 text-white hover:bg-white/10 font-semibold px-8 py-3 rounded-lg transition-all duration-300 text-center"
            >
              Contact Our Team
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}