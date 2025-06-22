import { Metadata } from 'next'
import CustomersPage from '@/components/CustomersPage'

export const metadata: Metadata = {
  title: 'Customers - ContentForge AI',
  description: 'Success stories and case studies from ContentForge AI customers. See how teams worldwide achieve remarkable results with our AI platform.',
  keywords: ['customer success', 'ai content case studies', 'testimonials', 'content creation results', 'customer stories'],
  openGraph: {
    title: 'Customers - ContentForge AI',
    description: 'Success stories from teams using ContentForge AI',
    url: '/customers',
  },
}

export default function Customers() {
  return <CustomersPage />
}