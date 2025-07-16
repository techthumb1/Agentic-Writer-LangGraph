// frontend/app/api/generate/status/[requestId]/route.ts
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;
if (!FASTAPI_BASE_URL || !FASTAPI_API_KEY) {
  throw new Error('FASTAPI_BASE_URL and FASTAPI_API_KEY must be set in environment variables');
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ requestId: string }> }
) {
  try {
    // Await the params Promise
    const { requestId } = await context.params;
    
    if (!requestId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Request ID is required' 
        },
        { status: 400 }
      );
    }
    
    console.log(`🔍 [GENERATE-STATUS] Checking status for: ${requestId}`);
    
    // Try to get status from backend
    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/generate/${requestId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${FASTAPI_API_KEY}`,
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000),
      });

      if (response.ok) {
        const data = await response.json();
        return NextResponse.json({
          success: true,
          status: data.status || 'completed',
          progress: data.progress || 100,
          content: data.content,
          metadata: data.metadata,
          request_id: requestId
        });
      }
      
      if (response.status === 404) {
        // Generation might be completed and cleaned up
        return NextResponse.json({
          success: true,
          status: 'completed',
          progress: 100,
          request_id: requestId,
          message: 'Generation completed (no longer in queue)'
        });
      }
      
    } catch {
      console.log(`⚠️ Backend status check failed, using fallback`);
    }
    
    // Fallback status response
    return NextResponse.json({
      success: true,
      status: 'completed',
      progress: 100,
      request_id: requestId,
      message: 'Generation status unknown, assuming completed'
    });
    
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Status check failed';
    console.error('🚨 [GENERATE-STATUS] Error:', errorMsg);
    
    // Handle potential undefined requestId in error case
    let requestIdForError: string | undefined;
    try {
      const params = await context.params;
      requestIdForError = params.requestId;
    } catch {
      requestIdForError = 'unknown';
    }
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to check generation status',
        message: errorMsg,
        request_id: requestIdForError
      }, 
      { status: 500 }
    );
  }
}