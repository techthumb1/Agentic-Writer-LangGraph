import React, { useState } from 'react';
import { 
  Check, 
  X, 
  Zap, 
  Star, 
  Users, 
  Shield, 
  Clock, 
  BarChart3,
  Headphones,
  Globe,
  Crown,
  Rocket
} from 'lucide-react';

const PricingPage = () => {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [hoveredPlan, setHoveredPlan] = useState<number | null>(null);

  const plans = [
    {
      name: 'Starter',
      description: 'Perfect for individuals and small projects',
      icon: Zap,
      price: {
        monthly: 29,
        yearly: 290 // 2 months free
      },
      popular: false,
      features: [
        { text: '10,000 words per month', included: true },
        { text: '5 content templates', included: true },
        { text: '3 style profiles', included: true },
        { text: 'Basic AI agents', included: true },
        { text: 'Email support', included: true },
        { text: 'Export to markdown', included: true },
        { text: 'Advanced agents', included: false },
        { text: 'Custom templates', included: false },
        { text: 'API access', included: false },
        { text: 'Priority support', included: false }
      ],
      cta: 'Start Free Trial',
      color: 'blue'
    },
    {
      name: 'Professional',
      description: 'Ideal for content creators and small teams',
      icon: Star,
      price: {
        monthly: 79,
        yearly: 790 // 2 months free
      },
      popular: true,
      features: [
        { text: '50,000 words per month', included: true },
        { text: 'Unlimited templates', included: true },
        { text: '10 style profiles', included: true },
        { text: 'All AI agents', included: true },
        { text: 'Priority email support', included: true },
        { text: 'Export to multiple formats', included: true },
        { text: 'Custom templates', included: true },
        { text: 'Collaboration tools', included: true },
        { text: 'Analytics dashboard', included: true },
        { text: 'API access', included: false },
        { text: 'White-label options', included: false }
      ],
      cta: 'Start Free Trial',
      color: 'purple'
    },
    {
      name: 'Enterprise',
      description: 'For large teams and organizations',
      icon: Crown,
      price: {
        monthly: 199,
        yearly: 1990 // 2 months free
      },
      popular: false,
      features: [
        { text: 'Unlimited words', included: true },
        { text: 'Unlimited templates', included: true },
        { text: 'Unlimited style profiles', included: true },
        { text: 'All AI agents + custom', included: true },
        { text: '24/7 priority support', included: true },
        { text: 'Advanced export options', included: true },
        { text: 'Custom integrations', included: true },
        { text: 'Advanced collaboration', included: true },
        { text: 'Advanced analytics', included: true },
        { text: 'Full API access', included: true },
        { text: 'White-label options', included: true },
        { text: 'Dedicated account manager', included: true }
      ],
      cta: 'Contact Sales',
      color: 'emerald'
    }
  ];

  const features = [
    {
      name: 'Multi-Agent Architecture',
      description: 'Specialized AI agents work together to create high-quality content',
      icon: Users
    },
    {
      name: 'Enterprise Security',
      description: 'SOC 2 compliant with end-to-end encryption',
      icon: Shield
    },
    {
      name: 'Lightning Fast',
      description: 'Generate content in seconds with our optimized infrastructure',
      icon: Clock
    },
    {
      name: 'Advanced Analytics',
      description: 'Track performance and optimize your content strategy',
      icon: BarChart3
    },
    {
      name: '24/7 Support',
      description: 'Get help when you need it with our dedicated support team',
      icon: Headphones
    },
    {
      name: 'Global Scale',
      description: 'Available worldwide with 99.9% uptime guarantee',
      icon: Globe
    }
  ];

  const getColorClasses = (color: string, isPrimary = false): string => {
    const colors: Record<string, string> = {
      blue: isPrimary ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'text-blue-600 border-blue-200',
      purple: isPrimary ? 'bg-purple-600 hover:bg-purple-700 text-white' : 'text-purple-600 border-purple-200',
      emerald: isPrimary ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'text-emerald-600 border-emerald-200'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Simple, transparent
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> pricing</span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
              Choose the perfect plan for your content creation needs. All plans include our powerful multi-agent AI system.
            </p>
            
            {/* Billing Toggle */}
            <div className="flex items-center justify-center mb-12">
              <div className="bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
                <button
                  onClick={() => setBillingPeriod('monthly')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    billingPeriod === 'monthly'
                      ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  Monthly
                </button>
                <button
                  onClick={() => setBillingPeriod('yearly')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    billingPeriod === 'yearly'
                      ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  Yearly
                  <span className="ml-2 bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded-full">
                    Save 17%
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => {
            const IconComponent = plan.icon;
            return (
              <div
                key={plan.name}
                onMouseEnter={() => setHoveredPlan(index)}
                onMouseLeave={() => setHoveredPlan(null)}
                className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg border-2 transition-all duration-300 ${
                  plan.popular 
                    ? 'border-purple-500 scale-105' 
                    : hoveredPlan === index 
                      ? 'border-gray-300 dark:border-gray-600 scale-102' 
                      : 'border-gray-200 dark:border-gray-700'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-gradient-to-r from-purple-500 to-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold flex items-center">
                      <Rocket className="w-4 h-4 mr-1" />
                      Most Popular
                    </div>
                  </div>
                )}
                
                <div className="p-8">
                  <div className="flex items-center mb-4">
                    <div className={`p-2 rounded-lg ${getColorClasses(plan.color)} bg-opacity-10`}>
                      <IconComponent className={`w-6 h-6 ${getColorClasses(plan.color)}`} />
                    </div>
                    <h3 className="ml-3 text-2xl font-bold text-gray-900 dark:text-white">
                      {plan.name}
                    </h3>
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-300 mb-6">
                    {plan.description}
                  </p>
                  
                  <div className="mb-6">
                    <div className="flex items-baseline">
                      <span className="text-4xl font-bold text-gray-900 dark:text-white">
                        ${plan.price[billingPeriod as keyof typeof plan.price]}
                      </span>
                      <span className="text-gray-600 dark:text-gray-300 ml-2">
                        /{billingPeriod === 'monthly' ? 'month' : 'year'}
                      </span>
                    </div>
                    {billingPeriod === 'yearly' && (
                      <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                        Save ${(plan.price.monthly * 12) - plan.price.yearly} per year
                      </p>
                    )}
                  </div>
                  
                  <button className={`w-full py-3 px-4 rounded-lg font-semibold transition-all duration-200 mb-6 ${
                    getColorClasses(plan.color, true)
                  }`}>
                    {plan.cta}
                  </button>
                  
                  <div className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center">
                        {feature.included ? (
                          <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                        ) : (
                          <X className="w-5 h-5 text-gray-300 dark:text-gray-600 mr-3 flex-shrink-0" />
                        )}
                        <span className={`text-sm ${
                          feature.included 
                            ? 'text-gray-700 dark:text-gray-300' 
                            : 'text-gray-400 dark:text-gray-600'
                        }`}>
                          {feature.text}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white dark:bg-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Everything you need to create amazing content
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Our platform combines cutting-edge AI technology with intuitive design to help you create content that converts.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div key={index} className="text-center p-6">
                  <div className="bg-blue-100 dark:bg-blue-900 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <IconComponent className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {feature.name}
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

      {/* FAQ Section */}
      <div className="bg-gray-50 dark:bg-gray-900 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Frequently asked questions
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Have questions? We have answers.
            </p>
          </div>
          
          <div className="space-y-6">
            {[
              {
                question: "Can I change my plan at any time?",
                answer: "Yes, you can upgrade or downgrade your plan at any time. Changes will be prorated and reflected in your next billing cycle."
              },
              {
                question: "What happens if I exceed my word limit?",
                answer: "If you exceed your monthly word limit, you can either upgrade your plan or purchase additional words as an add-on."
              },
              {
                question: "Do you offer refunds?",
                answer: "We offer a 30-day money-back guarantee for all paid plans. If you're not satisfied, contact us for a full refund."
              },
              {
                question: "Can I use ContentForge AI for commercial purposes?",
                answer: "Yes, all plans include commercial usage rights. You own the content generated and can use it for any commercial purpose."
              }
            ].map((faq, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {faq.question}
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;