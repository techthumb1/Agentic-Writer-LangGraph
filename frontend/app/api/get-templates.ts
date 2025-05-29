import { NextResponse } from 'next/server';
// Define TemplateMetadata type here if not exported from '@/types'
type TemplateMetadata = {
  id: string;
  title: string;
  description: string;
  category: string;
  styleProfileDefault: string;
  createdAt: Date;
  updatedAt: Date;
};

// Define APIResponse type here since it's not exported from '@/types'
type APIResponse<T> = {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: string;
  };
};

export async function GET() {
  try {
    const mockTemplates: TemplateMetadata[] = [
      {
        id: 'week_1',
        title: 'Federated Learning for Beginners',
        description: 'An introductory article template for explaining federated learning.',
        category: 'ml-basics',
        styleProfileDefault: 'educational_expert',
        createdAt: new Date('2024-01-01'),
        updatedAt: new Date('2024-01-02'),
      },
      {
        id: 'week_2',
        title: 'Contrastive Learning in Vision',
        description: 'Use this to generate content that introduces contrastive learning concepts.',
        category: 'deep-learning',
        styleProfileDefault: 'technical_dive',
        createdAt: new Date('2024-01-03'),
        updatedAt: new Date('2024-01-04'),
      }
    ];

    const response: APIResponse<TemplateMetadata[]> = {
      success: true,
      data: mockTemplates,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error fetching templates:', error);

    return NextResponse.json(
      {
        success: false,
        error: {
          code: 'FETCH_TEMPLATES_ERROR',
          message: 'Failed to fetch templates',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      },
      { status: 500 }
    );
  }
}
