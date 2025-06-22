import { Metadata } from 'next'
import PricingPage from '@/components/PricingPage'

export const metadata: Metadata = {
  title: 'Pricing - ContentForge AI',
  description: 'Simple, transparent pricing for AI-powered content creation. Choose the perfect plan for your content needs.',
  keywords: ['ai content pricing', 'content creation plans', 'ai writing cost', 'content automation pricing'],
  openGraph: {
    title: 'Pricing - ContentForge AI',
    description: 'Simple, transparent pricing for AI-powered content creation',
    url: '/pricing',
  },
}

export default function Pricing() {
  return <PricingPage />
}