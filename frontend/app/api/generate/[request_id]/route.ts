// frontend/app/api/generate/[request_id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ request_id: string }> }
) {
  try {
    const { request_id } = await params; // Await params as required by NextJS 15
    const requestId = request_id;

    if (!requestId) {
      return NextResponse.json(
        { success: false, error: 'Request ID is required' },
        { status: 400 }
      );
    }

    // Mock status check - in real implementation, check actual generation status
    // You could store generation status in database or cache
    const mockStatuses = ['pending', 'processing', 'completed', 'failed'];
    const randomStatus = mockStatuses[Math.floor(Math.random() * mockStatuses.length)];

    const mockResponse = {
      request_id: requestId,
      status: randomStatus,
      progress: randomStatus === 'completed' ? 100 : Math.floor(Math.random() * 90) + 10,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...(randomStatus === 'completed' && {
        content: {
          title: 'Generated Content Title',
          body: 'This is the generated content body...',
          word_count: 1250,
          template_used: 'test-template',
          style_profile_used: 'beginner_friendly'
        }
      }),
      ...(randomStatus === 'failed' && {
        error: 'Generation failed due to timeout'
      })
    };

    return NextResponse.json({
      success: true,
      data: mockResponse
    });

  } catch (error) {
    console.error('Generation status check error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to check generation status' },
      { status: 500 }
    );
  }
}