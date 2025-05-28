// frontend/app/api/templates/route.ts
import { NextResponse } from 'next/server';
import { ContentTemplate } from '@/types'; // Import your type

// In a real application, you would read these from your content_templates/*.yaml files
// For demonstration, we'll hardcode a few
const mockTemplates: ContentTemplate[] = [
  {
    id: 'blog_post_standard',
    name: 'Standard Blog Post',
    description: 'Generates a well-structured blog post on a given topic.',
    parameters: [
      { name: 'topic', label: 'Blog Post Topic', type: 'text', placeholder: 'e.g., The Future of AI in Healthcare' },
      { name: 'keywords', label: 'Target Keywords (comma-separated)', type: 'text', placeholder: 'e.g., AI, healthcare, innovation' },
      { name: 'audience', label: 'Target Audience', type: 'select', options: ['Beginner', 'Intermediate', 'Expert'], default: 'Intermediate' },
      { name: 'length', label: 'Desired Length (words)', type: 'number', default: 800 },
    ],
  },
  {
    id: 'research_summary',
    name: 'Research Paper Summary',
    description: 'Summarizes a research paper based on its abstract and key findings.',
    parameters: [
      { name: 'paper_title', label: 'Research Paper Title', type: 'text', placeholder: 'e.g., Contrastive Learning for Image Recognition' },
      { name: 'abstract_text', label: 'Abstract Text', type: 'textarea', placeholder: 'Paste abstract here...' },
      { name: 'key_findings', label: 'Key Findings (optional)', type: 'textarea', placeholder: 'Summarize key results if known...' },
    ],
  },
  {
    id: 'social_media_caption',
    name: 'Social Media Caption',
    description: 'Crafts engaging captions for social media posts.',
    parameters: [
      { name: 'main_message', label: 'Main Message', type: 'textarea', placeholder: 'What\'s the core idea?' },
      { name: 'platform', label: 'Platform', type: 'select', options: ['LinkedIn', 'Twitter', 'Instagram', 'Facebook'], default: 'LinkedIn' },
      { name: 'hashtags_count', label: 'Number of Hashtags', type: 'number', default: 5 },
    ],
  },
];

export async function GET() {
  return NextResponse.json(mockTemplates);
}
