import { NextRequest, NextResponse } from 'next/server';
import { APIResponse } from '@/types';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const res = await fetch(`${process.env.BACKEND_API_URL || 'http://localhost:5000'}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error('Backend generation failed');
    }

    const content = await res.json();

    const response: APIResponse<string> = {
      success: true,
      data: content,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error generating content:', error);

    return NextResponse.json(
      {
        success: false,
        error: {
          code: 'GENERATION_FAILED',
          message: 'Could not generate content',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      },
      { status: 500 }
    );
  }
}
