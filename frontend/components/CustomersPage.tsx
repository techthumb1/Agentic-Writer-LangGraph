import React, { useState } from 'react';
import Image from 'next/image';
import { 
  Star, 
  TrendingUp, 
  Users, 
  Clock, 
  ArrowRight, 
  Quote,
  Building2,
  BarChart3,
  CheckCircle,
  Award,
  Globe,
  Rocket,
  Target
} from 'lucide-react';

const CustomersPage = () => {
  const [activeTestimonial, setActiveTestimonial] = useState(0);

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Content Marketing Director",
      company: "TechFlow Inc.",
      image: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
      quote: "ContentForge AI has revolutionized our content strategy. We're producing 10x more content while maintaining quality and brand consistency.",
      rating: 5,
      metrics: {
        contentIncrease: "1000%",
        timeSaved: "75%",
        engagement: "250%"
      }
    },
    {
      name: "Marcus Rodriguez",
      role: "Founder & CEO",
      company: "StartupStory",
      image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
      quote: "As a startup, we needed to move fast with content. ContentForge AI helped us launch our content marketing in weeks, not months.",
      rating: 5,
      metrics: {
        launchTime: "80%",
        costs: "60%",
        output: "400%"
      }
    },
    {
      name: "Dr. Emily Watson",
      role: "Research Director",
      company: "MedTech Solutions",
      image: "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=150&h=150&fit=crop&crop=face",
      quote: "The accuracy and depth of medical content generated is impressive. It's like having a team of specialist writers at our fingertips.",
      rating: 5,
      metrics: {
        accuracy: "99%",
        compliance: "100%",
        efficiency: "300%"
      }
    }
  ];

  const caseStudies = [
    {
      company: "E-commerce Giant",
      industry: "Retail",
      logo: "🛒",
      challenge: "Needed to create product descriptions for 50,000+ items across multiple languages and markets.",
      solution: "Implemented ContentForge AI with custom templates and style profiles for each market segment.",
      results: [
        { metric: "50,000+", description: "Product descriptions created" },
        { metric: "15", description: "Languages supported" },
        { metric: "90%", description: "Reduction in content costs" },
        { metric: "6 weeks", description: "Project completion time" }
      ],
      testimonial: "ContentForge AI helped us scale our product content globally while maintaining local market relevance.",
      color: "blue"
    },
    {
      company: "FinTech Startup",
      industry: "Financial Services",
      logo: "💰",
      challenge: "Required compliance-heavy content for regulatory filings and customer communications.",
      solution: "Deployed enterprise solution with custom compliance checks and legal review workflows.",
      results: [
        { metric: "100%", description: "Compliance rate achieved" },
        { metric: "70%", description: "Faster regulatory submissions" },
        { metric: "45%", description: "Reduction in legal review time" },
        { metric: "$500K", description: "Annual savings on content creation" }
      ],
      testimonial: "The compliance features gave us confidence to automate our most critical communications.",
      color: "emerald"
    },
    {
      company: "Global Marketing Agency",
      industry: "Marketing & Advertising",
      logo: "📢",
      challenge: "Managing content for 200+ clients across diverse industries with consistent quality.",
      solution: "White-label implementation with client-specific workspaces and automated reporting.",
      results: [
        { metric: "200+", description: "Active client campaigns" },
        { metric: "500%", description: "Increase in content output" },
        { metric: "85%", description: "Client satisfaction rate" },
        { metric: "3x", description: "Agency revenue growth" }
      ],
      testimonial: "ContentForge AI became our secret weapon for scaling client services profitably.",
      color: "purple"
    }
  ];

  const stats = [
    { number: "10,000+", label: "Active Users", icon: Users },
    { number: "50M+", label: "Words Generated", icon: BarChart3 },
    { number: "99.9%", label: "Uptime", icon: CheckCircle },
    { number: "150+", label: "Countries", icon: Globe }
  ];

  const companies = [
    "TechFlow", "StartupStory", "MedTech Solutions", "GlobalCorp", "InnovateLab", 
    "FutureScale", "NextGen AI", "DataDriven Co", "CloudFirst", "AgileTeam"
  ];

  const getColorClasses = (color: string): string => {
    const colors: Record<string, string> = {
      blue: 'from-blue-500 to-blue-600',
      purple: 'from-purple-500 to-purple-600',
      emerald: 'from-emerald-500 to-emerald-600'
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
              Trusted by teams
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> worldwide</span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
              See how leading organizations use ContentForge AI to transform their content creation and achieve remarkable results.
            </p>
            
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
              {stats.map((stat, index) => {
                const IconComponent = stat.icon;
                return (
                  <div key={index} className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <IconComponent className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-2" />
                      <div className="text-3xl font-bold text-gray-900 dark:text-white">
                        {stat.number}
                      </div>
                    </div>
                    <div className="text-gray-600 dark:text-gray-300">
                      {stat.label}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Company Logos */}
      <div className="bg-white dark:bg-gray-800 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 dark:text-gray-400 mb-8">
            Trusted by innovative companies worldwide
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            {companies.map((company, index) => (
              <div key={index} className="bg-gray-100 dark:bg-gray-700 px-6 py-3 rounded-lg">
                <span className="text-gray-700 dark:text-gray-300 font-semibold">
                  {company}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="bg-gray-50 dark:bg-gray-900 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              What our customers say
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Real stories from real users achieving extraordinary results
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index}>
                <div
                  className={`bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg transition-all duration-300 ${
                    activeTestimonial === index ? 'ring-2 ring-blue-500 scale-105' : 'hover:shadow-xl'
                  }`}
                  onMouseEnter={() => setActiveTestimonial(index)}
                >
                  <Image
                    src={testimonial.image}
                    alt={testimonial.name}
                    width={64}
                    height={64}
                    className="w-16 h-16 rounded-full mr-4"
                  />
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {testimonial.name}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 text-sm">
                      {testimonial.role}
                    </p>
                    <p className="text-blue-600 dark:text-blue-400 text-sm font-medium">
                      {testimonial.company}
                    </p>
                  </div>
                  <div className="flex mb-4 mt-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <blockquote className="text-gray-700 dark:text-gray-300 mb-6 italic">
                    <Quote className="w-6 h-6 text-gray-400 mb-2" />
                    &ldquo;{testimonial.quote}&rdquo;
                  </blockquote>
                  <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    {Object.entries(testimonial.metrics).map(([key, value], metricIndex) => (
                      <div key={metricIndex} className="text-center">
                        <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                          {value}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                          {key.replace(/([A-Z])/g, ' $1')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Case Studies Section */}
      <div className="bg-white dark:bg-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Success stories
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Detailed case studies showing real-world impact and results
            </p>
          </div>

          <div className="space-y-12">
            {caseStudies.map((study, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Left Side - Challenge & Solution */}
                  <div>
                    <div className="flex items-center mb-6">
                      <div className="text-4xl mr-4">{study.logo}</div>
                      <div>
                        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                          {study.company}
                        </h3>
                        <p className="text-gray-600 dark:text-gray-300">
                          {study.industry}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-6">
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center">
                          <Target className="w-5 h-5 mr-2 text-red-500" />
                          Challenge
                        </h4>
                        <p className="text-gray-600 dark:text-gray-300">
                          {study.challenge}
                        </p>
                      </div>

                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center">
                          <Rocket className="w-5 h-5 mr-2 text-blue-500" />
                          Solution
                        </h4>
                        <p className="text-gray-600 dark:text-gray-300">
                          {study.solution}
                        </p>
                      </div>

                      <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-700 dark:text-gray-300">
                        &ldquo;{study.testimonial}&rdquo;
                      </blockquote>
                    </div>
                  </div>

                  {/* Right Side - Results */}
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                      <Award className="w-5 h-5 mr-2 text-emerald-500" />
                      Results Achieved
                    </h4>
                    
                    <div className="grid grid-cols-2 gap-6">
                      {study.results.map((result, resultIndex) => (
                        <div key={resultIndex} className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                          <div className={`text-3xl font-bold bg-gradient-to-r ${getColorClasses(study.color)} bg-clip-text text-transparent mb-2`}>
                            {result.metric}
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-300">
                            {result.description}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Industry Solutions */}
      <div className="bg-gray-50 dark:bg-gray-900 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Proven across industries
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              AgentWrite Pro adapts to your industry&#39;s unique requirements and standards
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: "🏥",
                industry: "Healthcare",
                description: "HIPAA-compliant content for medical communications, patient education, and research documentation.",
                features: ["Regulatory compliance", "Medical accuracy", "Patient-friendly language"]
              },
              {
                icon: "🏦",
                industry: "Financial Services",
                description: "SEC-compliant financial content, investment analysis, and customer communications.",
                features: ["Regulatory adherence", "Risk disclosures", "Professional tone"]
              },
              {
                icon: "🎓",
                industry: "Education",
                description: "Educational content, course materials, and academic research documentation.",
                features: ["Curriculum alignment", "Grade-level adaptation", "Learning objectives"]
              },
              {
                icon: "🏭",
                industry: "Manufacturing",
                description: "Technical documentation, safety manuals, and operational procedures.",
                features: ["Technical accuracy", "Safety compliance", "Clear instructions"]
              },
              {
                icon: "🛒",
                industry: "E-commerce",
                description: "Product descriptions, marketing copy, and customer support content.",
                features: ["SEO optimization", "Conversion focus", "Brand consistency"]
              },
              {
                icon: "⚖️",
                industry: "Legal",
                description: "Legal documents, contracts, and compliance materials with precision.",
                features: ["Legal accuracy", "Compliance checks", "Professional formatting"]
              }
            ].map((industry, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm hover:shadow-lg transition-shadow duration-200">
                <div className="text-4xl mb-4">{industry.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {industry.industry}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  {industry.description}
                </p>
                <ul className="space-y-2">
                  {industry.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                      <CheckCircle className="w-4 h-4 text-emerald-500 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Customer Success Metrics */}
      <div className="bg-white dark:bg-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Measurable impact
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Our customers consistently achieve remarkable improvements across key metrics
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                metric: "10x",
                description: "Faster content creation",
                icon: Clock,
                color: "blue"
              },
              {
                metric: "85%",
                description: "Reduction in content costs",
                icon: TrendingUp,
                color: "emerald"
              },
              {
                metric: "300%",
                description: "Increase in content output",
                icon: BarChart3,
                color: "purple"
              },
              {
                metric: "95%",
                description: "Customer satisfaction rate",
                icon: Star,
                color: "yellow"
              }
            ].map((stat, index) => {
              const IconComponent = stat.icon;
              return (
                <div key={index} className="text-center p-6 bg-gray-50 dark:bg-gray-900 rounded-xl">
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 ${
                    stat.color === 'blue' ? 'bg-blue-100 dark:bg-blue-900' :
                    stat.color === 'emerald' ? 'bg-emerald-100 dark:bg-emerald-900' :
                    stat.color === 'purple' ? 'bg-purple-100 dark:bg-purple-900' :
                    'bg-yellow-100 dark:bg-yellow-900'
                  }`}>
                    <IconComponent className={`w-8 h-8 ${
                      stat.color === 'blue' ? 'text-blue-600 dark:text-blue-400' :
                      stat.color === 'emerald' ? 'text-emerald-600 dark:text-emerald-400' :
                      stat.color === 'purple' ? 'text-purple-600 dark:text-purple-400' :
                      'text-yellow-600 dark:text-yellow-400'
                    }`} />
                  </div>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                    {stat.metric}
                  </div>
                  <div className="text-gray-600 dark:text-gray-300">
                    {stat.description}
                  </div>
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
            Join the success stories
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Start your journey to better content creation today and see results like our customers.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="inline-flex items-center px-8 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors duration-200">
              Start Free Trial
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
            <button className="inline-flex items-center px-8 py-3 border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-blue-600 transition-all duration-200">
              Schedule Demo
              <Building2 className="ml-2 w-5 h-5" />
            </button>
          </div>
          <p className="text-blue-100 text-sm mt-4">
            No credit card required • 14-day free trial • Setup in minutes
          </p>
        </div>
      </div>
    </div>
  );
};

export default CustomersPage;