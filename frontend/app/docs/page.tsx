// File: frontend/app/docs/page.tsx
// Enhanced Documentation page for AI Content Studio (Professional - No Emojis)

import { Metadata } from 'next';
import Link from 'next/link';
import { 
  Rocket, 
  Zap, 
  Network, 
  Palette, 
  MessageSquare, 
  Mail, 
  BookOpen,
  Play,
  Code,
  Database,
  Settings,
  BarChart3,
  Shield,
  Users,
  Clock,
  CheckCircle,
  Wrench,
  ExternalLink
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Documentation | AI Content Studio',
  description: 'Comprehensive documentation for AI Content Studio APIs, SDKs, and platform features.',
};

export default function DocsPage() {
  const quickStartGuides = [
    {
      title: 'Getting Started',
      description: 'Set up your first AI content generation workflow in under 5 minutes',
      icon: Rocket,
      time: '5 min',
      link: '/docs/getting-started'
    },
    {
      title: 'API Quick Start',
      description: 'Generate your first content using our REST API',
      icon: Zap,
      time: '10 min',
      link: '/docs/api/quickstart'
    },
    {
      title: 'LangGraph Integration',
      description: 'Build custom agent workflows with LangGraph',
      icon: Network,
      time: '15 min',
      link: '/docs/langgraph'
    },
    {
      title: 'Style Profiles',
      description: 'Create and customize content generation styles',
      icon: Palette,
      time: '8 min',
      link: '/docs/style-profiles'
    }
  ];

  const apiEndpoints = [
    {
      method: 'POST',
      endpoint: '/api/generate',
      description: 'Generate content using templates and style profiles',
      category: 'Content Generation'
    },
    {
      method: 'GET',
      endpoint: '/api/templates',
      description: 'List all available content templates',
      category: 'Templates'
    },
    {
      method: 'POST',
      endpoint: '/api/style-profiles',
      description: 'Create or update content style profiles',
      category: 'Style Profiles'
    },
    {
      method: 'GET',
      endpoint: '/api/status/{request_id}',
      description: 'Check generation status for long-running tasks',
      category: 'Status'
    },
    {
      method: 'POST',
      endpoint: '/api/langgraph/workflow',
      description: 'Execute custom LangGraph workflows',
      category: 'Workflows'
    },
    {
      method: 'GET',
      endpoint: '/api/health',
      description: 'Check system health and service status',
      category: 'System'
    }
  ];

  const sdkLanguages = [
    {
      name: 'Python',
      icon: Code,
      description: 'Full-featured SDK with async support and type hints',
      installCommand: 'pip install ai-content-studio',
      example: `from ai_content_studio import Client

client = Client(api_key="your-api-key")
content = await client.generate(
    template="blog_post",
    style_profile="technical_dive",
    topic="Machine Learning Trends 2025"
)`
    },
    {
      name: 'TypeScript/JavaScript',
      icon: Code,
      description: 'Modern SDK with full TypeScript support',
      installCommand: 'npm install @ai-content-studio/sdk',
      example: `import { AIContentStudio } from '@ai-content-studio/sdk';

const client = new AIContentStudio({ apiKey: 'your-api-key' });
const content = await client.generate({
  template: 'blog_post',
  styleProfile: 'technical_dive',
  topic: 'Machine Learning Trends 2025'
});`
    },
    {
      name: 'curl',
      icon: Database,
      description: 'Direct HTTP API access for any programming language',
      installCommand: 'curl (pre-installed on most systems)',
      example: `curl -X POST "https://api.aicontentstudio.com/generate" \\
  -H "Authorization: Bearer your-api-key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "template": "blog_post",
    "style_profile": "technical_dive",
    "topic": "Machine Learning Trends 2025"
  }'`
    }
  ];

  const features = [
    {
      title: 'Multi-Agent Workflows',
      description: 'Orchestrate complex content generation using specialized AI agents',
      icon: Users,
      docs: [
        'Agent Architecture Overview',
        'Custom Agent Development',
        'Workflow Orchestration',
        'Agent Communication Patterns'
      ]
    },
    {
      title: 'LangGraph Integration',
      description: 'Build sophisticated AI workflows with state management',
      icon: Network,
      docs: [
        'LangGraph Basics',
        'State Management',
        'Conditional Routing',
        'Error Handling'
      ]
    },
    {
      title: 'Content Templates',
      description: 'Pre-built templates for various content types and formats',
      icon: BookOpen,
      docs: [
        'Template Library',
        'Custom Templates',
        'Template Parameters',
        'Template Versioning'
      ]
    },
    {
      title: 'Style Profiles',
      description: 'Consistent content styling and voice across generations',
      icon: Palette,
      docs: [
        'Creating Style Profiles',
        'Style Inheritance',
        'Voice Customization',
        'Brand Guidelines'
      ]
    },
    {
      title: 'Enterprise Features',
      description: 'Advanced security, monitoring, and compliance features',
      icon: Shield,
      docs: [
        'SSO Integration',
        'Audit Logging',
        'Rate Limiting',
        'Data Governance'
      ]
    },
    {
      title: 'Real-time Monitoring',
      description: 'Monitor content generation performance and system health',
      icon: BarChart3,
      docs: [
        'Metrics Dashboard',
        'Alert Configuration',
        'Performance Monitoring',
        'Usage Analytics'
      ]
    }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Documentation
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Everything you need to integrate AI Content Studio into your applications. 
            From quick starts to advanced LangGraph workflows.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/docs/getting-started" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-lg transition-all duration-300">
              Get Started
            </Link>
            <Link href="/docs/api" className="border border-white/30 text-white hover:bg-white/10 font-semibold px-8 py-3 rounded-lg transition-all duration-300">
              API Reference
            </Link>
          </div>
        </div>

        {/* Quick Start Guides */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Quick Start Guides</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickStartGuides.map((guide, index) => (
              <Link key={index} href={guide.link} className="block">
                <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300 h-full">
                  <guide.icon className="w-8 h-8 text-purple-400 mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-3">{guide.title}</h3>
                  <p className="text-gray-300 mb-4">{guide.description}</p>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-purple-400" />
                    <span className="text-sm text-purple-400 font-medium">{guide.time} read</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* API Reference */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">API Reference</h2>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-white mb-4">Base URL</h3>
              <code className="bg-black/30 text-green-400 px-4 py-2 rounded-lg">
                https://api.aicontentstudio.com
              </code>
            </div>
            
            <h3 className="text-xl font-semibold text-white mb-6">Endpoints</h3>
            <div className="space-y-4">
              {apiEndpoints.map((endpoint, index) => (
                <div key={index} className="border border-white/20 rounded-lg p-4 hover:bg-white/5 transition-all duration-300">
                  <div className="flex flex-wrap items-center justify-between mb-2">
                    <div className="flex items-center gap-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        endpoint.method === 'GET' ? 'bg-green-500/20 text-green-400' :
                        endpoint.method === 'POST' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {endpoint.method}
                      </span>
                      <code className="text-gray-300 font-mono">{endpoint.endpoint}</code>
                    </div>
                    <span className="text-sm text-purple-400">{endpoint.category}</span>
                  </div>
                  <p className="text-gray-300">{endpoint.description}</p>
                </div>
              ))}
            </div>
            
            <div className="mt-6">
              <Link href="/docs/api/reference" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300 inline-flex items-center gap-2">
                View Full API Reference
                <ExternalLink className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* SDKs */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">SDKs & Libraries</h2>
          <div className="space-y-6">
            {sdkLanguages.map((sdk, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
                <div className="flex items-center gap-4 mb-4">
                  <sdk.icon className="w-8 h-8 text-purple-400" />
                  <div>
                    <h3 className="text-2xl font-semibold text-white">{sdk.name}</h3>
                    <p className="text-gray-300">{sdk.description}</p>
                  </div>
                </div>
                
                <div className="grid lg:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">Installation</h4>
                    <code className="block bg-black/30 text-green-400 p-4 rounded-lg overflow-x-auto">
                      {sdk.installCommand}
                    </code>
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">Example Usage</h4>
                    <pre className="bg-black/30 text-gray-300 p-4 rounded-lg overflow-x-auto text-sm">
                      {sdk.example}
                    </pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Features Documentation */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Feature Documentation</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                <feature.icon className="w-8 h-8 text-purple-400 mb-4" />
                <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-300 mb-4">{feature.description}</p>
                <div className="space-y-2">
                  {feature.docs.map((doc, docIndex) => (
                    <Link key={docIndex} href={`/docs/${feature.title.toLowerCase().replace(/\s+/g, '-')}/${doc.toLowerCase().replace(/\s+/g, '-')}`} className="text-sm text-purple-400 hover:text-purple-300 transition-colors flex items-center gap-2">
                      <ExternalLink className="w-3 h-3" />
                      {doc}
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Support Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Need Help?</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center">
              <MessageSquare className="w-8 h-8 text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-3">Community</h3>
              <p className="text-gray-300 mb-4">Join our Discord community for discussions and support</p>
              <Link href="/community" className="text-purple-400 hover:text-purple-300 font-medium inline-flex items-center gap-2">
                Join Discord
                <ExternalLink className="w-4 h-4" />
              </Link>
            </div>
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center">
              <Mail className="w-8 h-8 text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-3">Support</h3>
              <p className="text-gray-300 mb-4">Get direct help from our support team</p>
              <Link href="/contact" className="text-purple-400 hover:text-purple-300 font-medium inline-flex items-center gap-2">
                Contact Support
                <ExternalLink className="w-4 h-4" />
              </Link>
            </div>
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center">
              <Play className="w-8 h-8 text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-3">Tutorials</h3>
              <p className="text-gray-300 mb-4">Step-by-step video tutorials and guides</p>
              <Link href="/docs/tutorials" className="text-purple-400 hover:text-purple-300 font-medium inline-flex items-center gap-2">
                Watch Tutorials
                <ExternalLink className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* Latest Updates */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-4">Latest Updates</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-sm font-medium flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  NEW
                </span>
                <div>
                  <h3 className="text-white font-semibold">LangGraph v2.0 Integration</h3>
                  <p className="text-gray-300 text-sm">Enhanced workflow orchestration with improved state management</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-sm font-medium flex items-center gap-1">
                  <Settings className="w-3 h-3" />
                  UPDATE
                </span>
                <div>
                  <h3 className="text-white font-semibold">Python SDK v1.5.0</h3>
                  <p className="text-gray-300 text-sm">Added async batch processing and improved error handling</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded text-sm font-medium flex items-center gap-1">
                  <Wrench className="w-3 h-3" />
                  FIX
                </span>
                <div>
                  <h3 className="text-white font-semibold">API Rate Limiting</h3>
                  <p className="text-gray-300 text-sm">Improved rate limiting behavior for enterprise customers</p>
                </div>
              </div>
            </div>
            <Link href="/docs/changelog" className="text-purple-400 hover:text-purple-300 font-medium inline-flex items-center gap-2 mt-6">
              View Full Changelog
              <ExternalLink className="w-4 h-4" />
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}