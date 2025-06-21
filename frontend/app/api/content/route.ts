// frontend/app/api/content/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    // This would typically fetch from your database
    // For now, returning mock data based on your project structure
    const mockContent = [
      {
        id: '1',
        title: 'An Introduction to Contrastive Learning',
        template: '2025-05-27_an_introduction_to_contrastive_learning',
        status: 'completed',
        created_at: new Date().toISOString(),
        content_preview: 'Contrastive learning has emerged as a powerful paradigm...'
      },
      {
        id: '2',
        title: 'Federated Learning 101',
        template: 'federated_learning_101',
        status: 'completed',
        created_at: new Date().toISOString(),
        content_preview: 'Federated learning enables machine learning...'
      },
      {
        id: '3',
        title: 'Future of LLMs',
        template: 'future_of_llms',
        status: 'draft',
        created_at: new Date().toISOString(),
        content_preview: 'Large Language Models are rapidly evolving...'
      }
    ];

    return NextResponse.json({
      success: true,
      content: mockContent,
      total: mockContent.length
    });

  } catch (error) {
    console.error('Content API error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch content' },
      { status: 500 }
    );
  }
}

// POST endpoint for creating new content
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.title || !body.template) {
      return NextResponse.json(
        { success: false, error: 'Title and template are required' },
        { status: 400 }
      );
    }

    // Mock creation - in real implementation, save to database
    const newContent = {
      id: Date.now().toString(),
      title: body.title,
      template: body.template,
      status: 'draft',
      created_at: new Date().toISOString(),
      content: body.content || '',
      style_profile: body.style_profile || 'beginner_friendly'
    };

    return NextResponse.json({
      success: true,
      content: newContent,
      message: 'Content created successfully'
    });

  } catch (error) {
    console.error('Content creation error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create content' },
      { status: 500 }
    );
  }
}