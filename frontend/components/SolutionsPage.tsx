import React, { useState } from 'react';
import { 
  Users, 
  Building2, 
  Target, 
  Clock, 
  Shield, 
  ChevronRight,
  ArrowRight,
  CheckCircle,
  Lightbulb,
  Megaphone,
  Globe,
  Briefcase
} from 'lucide-react';

const SolutionsPage = () => {
  const [activeSolution, setActiveSolution] = useState(0);

  const solutions = [
    {
      id: 'marketing',
      title: 'Marketing Teams',
      subtitle: 'Scale your content marketing with AI-powered efficiency',
      icon: Megaphone,
      color: 'blue',
      description: 'Empower your marketing team to create compelling content at scale while maintaining brand consistency and quality.',
      features: [
        'Brand-consistent content generation',
        'Social media content automation',
        'Email campaign creation',
        'Blog post and article writing',
        'Ad copy optimization',
        'Content calendar integration'
      ],
      benefits: [
        { metric: '10x', description: 'faster content creation' },
        { metric: '85%', description: 'reduction in content costs' },
        { metric: '300%', description: 'increase in content output' }
      ],
      useCases: [
        'Social media campaigns',
        'Email marketing sequences',
        'Blog content strategy',
        'Product launch materials',
        'SEO-optimized articles'
      ]
    },
    {
      id: 'creators',
      title: 'Content Creators',
      subtitle: 'Transform your creative workflow with intelligent assistance',
      icon: Lightbulb,
      color: 'purple',
      description: 'Break through creative blocks and maintain consistent publishing schedules with AI that understands your unique voice.',
      features: [
        'Personal writing style adaptation',
        'Content ideation and brainstorming',
        'Multi-format content creation',
        'Research and fact-checking',
        'SEO optimization',
        'Publishing workflow automation'
      ],
      benefits: [
        { metric: '5x', description: 'more content published' },
        { metric: '70%', description: 'time saved on research' },
        { metric: '200%', description: 'engagement increase' }
      ],
      useCases: [
        'YouTube video scripts',
        'Newsletter content',
        'Course materials',
        'Social media posts',
        'Podcast show notes'
      ]
    },
    {
      id: 'enterprise',
      title: 'Enterprise',
      subtitle: 'Enterprise-grade content solutions for large organizations',
      icon: Building2,
      color: 'emerald',
      description: 'Deploy AI-powered content creation across your organization with enterprise security, compliance, and scalability.',
      features: [
        'Enterprise security & compliance',
        'Custom AI model training',
        'Advanced workflow automation',
        'Team collaboration tools',
        'API integration capabilities',
        'White-label solutions'
      ],
      benefits: [
        { metric: '60%', description: 'reduction in content costs' },
        { metric: '40%', description: 'faster time-to-market' },
        { metric: '99.9%', description: 'uptime guarantee' }
      ],
      useCases: [
        'Technical documentation',
        'Training materials',
        'Internal communications',
        'Product documentation',
        'Compliance reports'
      ]
    },
    {
      id: 'agencies',
      title: 'Agencies',
      subtitle: 'Deliver exceptional client results with AI-powered content',
      icon: Briefcase,
      color: 'orange',
      description: 'Scale your agency operations and deliver consistent, high-quality content for multiple clients simultaneously.',
      features: [
        'Multi-client workspace management',
        'Client-specific style profiles',
        'Collaborative review workflows',
        'Performance analytics',
        'White-label reporting',
        'Bulk content generation'
      ],
      benefits: [
        { metric: '4x', description: 'more clients served' },
        { metric: '50%', description: 'improved profit margins' },
        { metric: '90%', description: 'client satisfaction rate' }
      ],
      useCases: [
        'Client content campaigns',
        'Multi-brand management',
        'Pitch deck creation',
        'Case study development',
        'Client reporting'
      ]
    }
  ];

  const getColorClasses = (color: string): string => {
    const colors: Record<string, string> = {
      blue: 'from-blue-500 to-blue-600',
      purple: 'from-purple-500 to-purple-600',
      emerald: 'from-emerald-500 to-emerald-600',
      orange: 'from-orange-500 to-orange-600'
    };
    return colors[color] || colors.blue;
  };

  const getTextColorClasses = (color: string): string => {
    const colors: Record<string, string> = {
      blue: 'text-blue-600',
      purple: 'text-purple-600',
      emerald: 'text-emerald-600',
      orange: 'text-orange-600'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Solutions for every
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> content need</span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
              Discover how ContentForge AI transforms content creation across different industries and use cases with our intelligent multi-agent system.
            </p>
          </div>
        </div>
      </div>

      {/* Solution Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex flex-wrap justify-center gap-4 mb-16">
          {solutions.map((solution, index) => {
            const IconComponent = solution.icon;
            return (
              <button
                key={solution.id}
                onClick={() => setActiveSolution(index)}
                className={`flex items-center px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                  activeSolution === index
                    ? `bg-gradient-to-r ${getColorClasses(solution.color)} text-white shadow-lg`
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                <IconComponent className="w-5 h-5 mr-2" />
                {solution.title}
              </button>
            );
          })}
        </div>

        {/* Active Solution Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div>
            <div className="flex items-center mb-6">
              <div className={`p-3 rounded-lg bg-gradient-to-r ${getColorClasses(solutions[activeSolution].color)} text-white`}>
                {React.createElement(solutions[activeSolution].icon, { className: "w-8 h-8" })}
              </div>
              <div className="ml-4">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {solutions[activeSolution].title}
                </h2>
                <p className={`text-lg ${getTextColorClasses(solutions[activeSolution].color)}`}>
                  {solutions[activeSolution].subtitle}
                </p>
              </div>
            </div>

            <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
              {solutions[activeSolution].description}
            </p>

            {/* Benefits */}
            <div className="grid grid-cols-3 gap-6 mb-8">
              {solutions[activeSolution].benefits.map((benefit, index) => (
                <div key={index} className="text-center">
                  <div className={`text-3xl font-bold ${getTextColorClasses(solutions[activeSolution].color)} mb-1`}>
                    {benefit.metric}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">
                    {benefit.description}
                  </div>
                </div>
              ))}
            </div>

            <button className={`inline-flex items-center px-6 py-3 bg-gradient-to-r ${getColorClasses(solutions[activeSolution].color)} text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-200`}>
              Get Started
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
          </div>

          {/* Right Content - Features & Use Cases */}
          <div className="space-y-8">
            {/* Features */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <CheckCircle className={`w-6 h-6 mr-2 ${getTextColorClasses(solutions[activeSolution].color)}`} />
                Key Features
              </h3>
              <div className="space-y-3">
                {solutions[activeSolution].features.map((feature, index) => (
                  <div key={index} className="flex items-center">
                    <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${getColorClasses(solutions[activeSolution].color)} mr-3`} />
                    <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Use Cases */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Target className={`w-6 h-6 mr-2 ${getTextColorClasses(solutions[activeSolution].color)}`} />
                Common Use Cases
              </h3>
              <div className="space-y-3">
                {solutions[activeSolution].useCases.map((useCase, index) => (
                  <div key={index} className="flex items-center">
                    <ChevronRight className={`w-4 h-4 mr-2 ${getTextColorClasses(solutions[activeSolution].color)}`} />
                    <span className="text-gray-700 dark:text-gray-300">{useCase}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Why Choose Us Section */}
      <div className="bg-gray-50 dark:bg-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Why choose ContentForge AI?
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Our multi-agent architecture and advanced AI capabilities set us apart from traditional content generation tools.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: Users,
                title: 'Multi-Agent Intelligence',
                description: 'Specialized AI agents collaborate to create higher-quality content than single-model approaches.'
              },
              {
                icon: Clock,
                title: 'Lightning Fast',
                description: 'Generate high-quality content in seconds, not hours, with our optimized infrastructure.'
              },
              {
                icon: Shield,
                title: 'Enterprise Security',
                description: 'SOC 2 compliant with enterprise-grade security and data protection measures.'
              },
              {
                icon: Globe,
                title: 'Global Scale',
                description: 'Available worldwide with 99.9% uptime and support for multiple languages and regions.'
              }
            ].map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div key={index} className="text-center">
                  <div className="bg-white dark:bg-gray-700 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                    <IconComponent className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-16">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to transform your content creation?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of teams already using ContentForge AI to create better content faster.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors duration-200">
              Start Free Trial
            </button>
            <button className="px-8 py-3 border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-blue-600 transition-all duration-200">
              Schedule Demo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SolutionsPage;