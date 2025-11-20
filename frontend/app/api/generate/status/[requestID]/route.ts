// frontend/app/api/generate/status/[requestId]/route.ts
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://127.0.0.1:8000';
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ requestId: string }> }
) {
  // ✅ FIX: await params in Next.js 15
  const { requestId } = await context.params;

  try {
    const backendUrl = `${FASTAPI_BASE_URL}/api/generate/status/${requestId}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (FASTAPI_API_KEY) {
      headers['Authorization'] = `Bearer ${FASTAPI_API_KEY}`;
    }

    console.log(`🔍 [STATUS] Checking backend: ${backendUrl}`);

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers,
      cache: 'no-cache'
    });

    if (!response.ok) {
      console.error(`❌ [STATUS] Backend error: ${response.status}`);
      return NextResponse.json(
        {
          success: false,
          error: `Backend unavailable (${response.status})`,
          request_id: requestId
        },
        { status: 502 }
      );
    }

    const data = await response.json();
    
    const status = data.success ? data.data?.status || 'unknown' : 'failed';
    const content = data.success ? data.data?.content || '' : '';
    const metadata = data.success ? data.data?.metadata || {} : {};
    const progress = data.success ? data.data?.progress || 0 : 0;

    console.log(`✅ [STATUS] ${requestId}: ${status}, content: ${content.length} chars`);

    return NextResponse.json({
      success: true,
      data: {
        request_id: requestId,
        status,
        content,
        metadata,
        progress
      }
    });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error(`❌ [STATUS] Failed for ${requestId}: ${errorMessage}`);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Status check failed',
        message: errorMessage,
        request_id: requestId
      },
      { status: 500 }
    );
  }
}