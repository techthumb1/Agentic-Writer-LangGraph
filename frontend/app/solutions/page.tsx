import { Metadata } from 'next'
import SolutionsPage from '@/components/SolutionsPage'

export const metadata: Metadata = {
  title: 'Solutions - ContentForge AI',
  description: 'AI content solutions for marketing teams, content creators, enterprises, and agencies. Discover how our multi-agent system transforms content creation.',
  keywords: ['ai content solutions', 'marketing automation', 'enterprise content', 'agency tools', 'content marketing'],
  openGraph: {
    title: 'Solutions - ContentForge AI',
    description: 'AI content solutions for every team and industry',
    url: '/solutions',
  },
}

export default function Solutions() {
  return <SolutionsPage />
}