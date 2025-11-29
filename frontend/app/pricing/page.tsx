"use client"

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { 
  ArrowRight, 
  Check, 
  Star,
  Zap,
  Crown,
  Rocket
} from 'lucide-react';

export default function PricingPage() {
  const plans = [
    {
      name: "Starter",
      price: "Free",
      period: "forever",
      description: "Perfect for individuals getting started with AI content creation",
      features: [
        "5 content generations per month",
        "Basic templates",
        "Standard AI models",
        "Email support",
        "Basic export options"
      ],
      cta: "Get Started Free",
      href: "/auth/signin",
      popular: false,
      icon: Zap
    },
    {
      name: "Professional",
      price: "$29",
      period: "per month",
      description: "Ideal for content creators and small businesses",
      features: [
        "100 content generations per month",
        "Advanced templates",
        "Premium AI models",
        "Priority support",
        "Advanced export options",
        "Custom style profiles",
        "Team collaboration (up to 3 users)"
      ],
      cta: "Start Free Trial",
      href: "/auth/signin",
      popular: true,
      icon: Crown
    },
    {
      name: "Enterprise",
      price: "$99",
      period: "per month",
      description: "For large teams and organizations with advanced needs",
      features: [
        "Unlimited content generations",
        "Custom templates",
        "White-label options",
        "24/7 premium support",
        "API access",
        "Advanced analytics",
        "Unlimited team members",
        "Custom integrations",
        "Dedicated account manager"
      ],
      cta: "Contact Sales",
      href: "/contact",
      popular: false,
      icon: Rocket
    }
  ];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-6xl mx-auto text-white">
        {/* Page Header */}
        <header className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6">
            Simple, Transparent
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
              {" "}Pricing
            </span>
          </h1>
          <p className="text-xl text-gray-300 leading-relaxed max-w-3xl mx-auto">
            Choose the perfect plan for your content creation needs. Start free and scale as you grow.
          </p>
        </header>

        {/* Pricing Cards */}
<div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
  {plans.map((plan) => {
    const IconComponent = plan.icon;
    return (
      <div
        key={plan.name}
        className={`relative bg-white/10 backdrop-blur-sm border rounded-xl p-8 hover:bg-white/15 transition-all duration-300 transform hover:scale-105 flex flex-col h-full ${
          plan.popular 
            ? 'border-purple-400 ring-2 ring-purple-400/20' 
            : 'border-white/20'
        }`}
      >
        {plan.popular && (
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-1 rounded-full text-sm font-medium flex items-center">
              <Star className="h-4 w-4 mr-1" />
              Most Popular
            </div>
          </div>
        )}
        
        <div className="text-center">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
            plan.popular 
              ? 'bg-gradient-to-r from-purple-500 to-pink-500' 
              : 'bg-gray-700'
          }`}>
            <IconComponent className="h-8 w-8 text-white" />
          </div>
          
          <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
          <div className="mb-4">
            <span className="text-4xl font-bold">{plan.price}</span>
            {plan.price !== "Free" && (
              <span className="text-gray-400 ml-1">/{plan.period}</span>
            )}
          </div>
          <p className="text-gray-300 text-sm mb-6">{plan.description}</p>
        </div>

        <ul className="space-y-3 mb-8 flex-grow">
          {plan.features.map((feature, featureIndex) => (
            <li key={featureIndex} className="flex items-start">
              <Check className="h-5 w-5 text-green-400 mt-0.5 mr-3 flex-shrink-0" />
              <span className="text-gray-300 text-sm">{feature}</span>
            </li>
          ))}
        </ul>

        <div className="mt-auto">
          <Link href={plan.href} className="block">
            <Button
              className={`w-full py-3 rounded-lg font-semibold transition-all duration-300 ${
                plan.popular
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white'
                  : 'bg-white/10 hover:bg-white/20 text-white border border-white/20'
              }`}
            >
              {plan.cta}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>
    );
  })}
</div>

        {/* FAQ Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-3">Can I change plans anytime?</h3>
              <p className="text-gray-300 text-sm">Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.</p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-3">Is there a free trial?</h3>
              <p className="text-gray-300 text-sm">Yes, all paid plans come with a 14-day free trial. No credit card required to start.</p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-3">What payment methods do you accept?</h3>
              <p className="text-gray-300 text-sm">We accept all major credit cards, PayPal, and bank transfers for enterprise plans.</p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-3">Can I cancel anytime?</h3>
              <p className="text-gray-300 text-sm">Absolutely. You can cancel your subscription at any time with no cancellation fees.</p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
          <h2 className="text-2xl sm:text-3xl font-bold mb-4">
            Ready to Transform Your Content Creation?
          </h2>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Join thousands of content creators who are already using our platform to create exceptional content.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signin" passHref>
              <Button
                size="lg"
                className="w-full sm:w-auto bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/contact" passHref>
              <Button
                size="lg"
                variant="outline"
                className="w-full sm:w-auto border-purple-400 text-purple-500 hover:bg-purple-900/20 border-2 font-semibold px-8 py-3 rounded-full shadow-md transition-all duration-300 hover:scale-105"
              >
                Contact Sales
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}