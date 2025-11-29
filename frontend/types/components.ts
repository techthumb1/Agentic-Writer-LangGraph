import { LucideIcon } from 'lucide-react';

// Pricing Page Types
export interface PricingPlan {
  name: string;
  description: string;
  icon: LucideIcon;
  price: {
    monthly: number;
    yearly: number;
  };
  popular: boolean;
  features: Array<{
    text: string;
    included: boolean;
  }>;
  cta: string;
  color: 'blue' | 'purple' | 'emerald';
}

export interface PricingFeature {
  name: string;
  description: string;
  icon: LucideIcon;
}

// Solutions Page Types
export interface Solution {
  id: string;
  title: string;
  subtitle: string;
  icon: LucideIcon;
  color: 'blue' | 'purple' | 'emerald' | 'orange';
  description: string;
  features: string[];
  benefits: Array<{
    metric: string;
    description: string;
  }>;
  useCases: string[];
}

// Customers Page Types
export interface Testimonial {
  name: string;
  role: string;
  company: string;
  image: string;
  quote: string;
  rating: number;
  metrics: Record<string, string>;
}

export interface CaseStudy {
  company: string;
  industry: string;
  logo: string;
  challenge: string;
  solution: string;
  results: Array<{
    metric: string;
    description: string;
  }>;
  testimonial: string;
  color: 'blue' | 'purple' | 'emerald';
}

export interface Statistic {
  number: string;
  label: string;
  icon: LucideIcon;
}

export interface IndustryInfo {
  icon: string;
  industry: string;
  description: string;
  features: string[];
}