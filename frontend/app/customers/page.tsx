"use client"

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { 
  ArrowRight, 
  Quote,
  Star,
  Users,
  Building2,
  Briefcase,
  GraduationCap,
  Newspaper,
  TrendingUp
} from 'lucide-react';

export default function CustomersPage() {
  const testimonials = [
    {
      name: "Maggie Kaufman",
      title: "Content Marketing Manager",
      company: "ProLyfic Solutions",
      image: "SC",
      rating: 5,
      quote: "WriterzRoom has revolutionized our content creation process. We're producing 3x more high-quality content in half the time. The AI understands our brand voice perfectly.",
      industry: "Technology"
    },
    {
      name: "Dr. Michael J. Schillingsberg",
      title: "Research Director",
      company: "University Research Lab",
      image: "MR",
      rating: 4.5,
      quote: "The research summarization capabilities are incredible. What used to take days now takes hours, and the quality is consistently excellent. A game-changer for academic work.",
      industry: "Education"
    },
    {
      name: "Caroline Miller",
      title: "Founder & CEO",
      company: "MA-Schultz Production",
      image: "EW",
      rating: 5,
      quote: "As a startup founder, time is everything. WriterzRoom helps me create professional content for investors, customers, and partners without hiring a full marketing team.",
      industry: "Startup"
    },
    {
      name: "Johnathan Howard",
      title: "Senior Analyst",
      company: "Financial Insights Corp",
      image: "JP",
      rating: 4.0,
      quote: "The business intelligence features are outstanding. Our reports are more comprehensive and data-driven than ever before. Clients love the improved quality.",
      industry: "Finance"
    },
    {
      name: "Stacey Van Horn",
      title: "Technical Writer",
      company: "DevTools Inc",
      image: "LT",
      rating: 4.5,
      quote: "Creating technical documentation used to be a bottleneck. Now our developer docs are always up-to-date and user-friendly. The AI understands complex technical concepts.",
      industry: "Software"
    },
    {
      name: "Ronauld Stewart",
      title: "Marketing Director",
      company: "E-commerce Giant",
      image: "DK",
      rating: 4.5,
      quote: "We manage thousands of product descriptions and marketing campaigns. WriterzRoom scales with us perfectly, maintaining quality across all our content.",
      industry: "E-commerce"
    }
  ];

  const industries = [
    {
      name: "Technology",
      icon: Building2,
      description: "Software companies, SaaS platforms, and tech startups",
      useCases: ["Technical documentation", "Product descriptions", "Developer guides"]
    },
    {
      name: "Education",
      icon: GraduationCap,
      description: "Universities, research institutions, and educational platforms",
      useCases: ["Research summaries", "Course materials", "Academic papers"]
    },
    {
      name: "Finance",
      icon: TrendingUp,
      description: "Banks, investment firms, and fintech companies",
      useCases: ["Market analysis", "Investment reports", "Compliance documentation"]
    },
    {
      name: "Healthcare",
      icon: Users,
      description: "Hospitals, medical research, and healthcare technology",
      useCases: ["Medical content", "Patient education", "Research publications"]
    },
    {
      name: "Media & Publishing",
      icon: Newspaper,
      description: "Publishing houses, media companies, and content agencies",
      useCases: ["Articles", "News content", "Editorial pieces"]
    },
    {
      name: "Consulting",
      icon: Briefcase,
      description: "Management consulting, strategy firms, and professional services",
      useCases: ["Client reports", "Proposals", "Strategy documents"]
    }
  ];

  const stats = [
    { number: "1,000+", label: "Active Users", description: "Content creators worldwide" },
    { number: "50K+", label: "Content Pieces", description: "Generated monthly" },
    { number: "95%", label: "Satisfaction Rate", description: "Customer satisfaction" },
    { number: "40%", label: "Time Saved", description: "Average productivity gain" }
  ];

  // Helper function to render star ratings with decimal support
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    // Add full stars
    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <Star key={`full-${i}`} className="h-4 w-4 text-yellow-400 fill-current" />
      );
    }

    // Add half star if needed
    if (hasHalfStar) {
      stars.push(
        <div key="half" className="relative">
          <Star className="h-4 w-4 text-gray-300" />
          <div className="absolute top-0 left-0 w-1/2 overflow-hidden">
            <Star className="h-4 w-4 text-yellow-400 fill-current" />
          </div>
        </div>
      );
    }

    // Add empty stars to make it 5 total
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <Star key={`empty-${i}`} className="h-4 w-4 text-gray-300" />
      );
    }

    return stars;
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-6xl mx-auto text-white">
        {/* Page Header */}
        <header className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6">
            Trusted by
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
              {" "}Industry Leaders
            </span>
          </h1>
          <p className="text-xl text-gray-300 leading-relaxed max-w-3xl mx-auto">
            See how organizations across industries are transforming their content creation with WriterzRoom.
          </p>
        </header>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {stats.map((stat, index) => (
            <div key={index} className="text-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
              <div className="text-3xl sm:text-4xl font-bold text-purple-400 mb-2">{stat.number}</div>
              <div className="text-lg font-semibold mb-1">{stat.label}</div>
              <div className="text-sm text-gray-400">{stat.description}</div>
            </div>
          ))}
        </div>

        {/* Industries Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Industries We Serve</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {industries.map((industry, index) => {
              const IconComponent = industry.icon;
              return (
                <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                  <div className="flex items-center mb-4">
                    <div className="bg-purple-600 w-10 h-10 rounded-lg flex items-center justify-center mr-3">
                      <IconComponent className="h-5 w-5 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold">{industry.name}</h3>
                  </div>
                  <p className="text-gray-300 text-sm mb-4">{industry.description}</p>
                  <div className="space-y-1">
                    {industry.useCases.map((useCase, ucIndex) => (
                      <div key={ucIndex} className="text-xs text-purple-300">• {useCase}</div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Testimonials Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">What Our Customers Say</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-pink-600 rounded-full flex items-center justify-center text-white font-bold mr-4">
                    {testimonial.image}
                  </div>
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-gray-400">{testimonial.title}</div>
                    <div className="text-xs text-purple-300">{testimonial.company}</div>
                  </div>
                </div>
                
                <div className="flex mb-3">
                  {renderStars(testimonial.rating)}
                  <span className="ml-2 text-sm text-gray-400">({testimonial.rating})</span>
                </div>
                
                <Quote className="h-6 w-6 text-purple-400 mb-2" />
                <p className="text-gray-300 text-sm italic leading-relaxed">&quot;{testimonial.quote}&quot;</p>
                
                <div className="mt-4 text-xs text-purple-300 font-medium">
                  {testimonial.industry} Industry
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Case Study Preview */}
        <div className="mb-16">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold mb-4">Success Story: ProLyfic Solutions</h2>
                <p className="text-gray-300 mb-4">
                  See how ProLyfic Solutions increased their content output by 250% while maintaining 
                  quality and reducing costs by 40% using WriterzRoom.
                </p>
                <ul className="space-y-2 mb-6">
                  <li className="flex items-center text-sm">
                    <TrendingUp className="h-4 w-4 text-green-400 mr-2" />
                    250% increase in content production
                  </li>
                  <li className="flex items-center text-sm">
                    <TrendingUp className="h-4 w-4 text-green-400 mr-2" />
                    40% reduction in content creation costs
                  </li>
                  <li className="flex items-center text-sm">
                    <TrendingUp className="h-4 w-4 text-green-400 mr-2" />
                    50% faster time-to-market for campaigns
                  </li>
                </ul>
                <Link href="/case-studies/prolyfic-solutions">
                  <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
                    Read Full Case Study
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
              <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 rounded-lg p-6 border border-purple-400/20">
                <div className="text-center">
                  <div className="text-4xl font-bold text-purple-400 mb-2">250%</div>
                  <div className="text-sm text-gray-300">Content Increase</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
          <h2 className="text-2xl sm:text-3xl font-bold mb-4">
            Join Our Growing Community
          </h2>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Ready to transform your content creation process? Join thousands of satisfied customers 
            who are already creating exceptional content with WriterzRoom.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signin" passHref>
              <Button
                size="lg"
                className="w-full sm:w-auto bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                Start Your Journey
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