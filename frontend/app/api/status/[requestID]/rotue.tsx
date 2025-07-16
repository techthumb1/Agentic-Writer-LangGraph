// frontend/app/api/generate/status/[requestId]/route.ts

import { NextRequest, NextResponse } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: { requestId: string } }
) {
  try {
    const { requestId } = params;
    
    console.log(`🔍 Checking status for request: ${requestId}`);

    // Forward the status check to your backend - FIXED URL
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const backendStatusUrl = `${backendUrl}/status/${requestId}`;
    
    console.log('🔍 [STATUS] Calling backend URL:', backendStatusUrl);
    
    const statusResponse = await fetch(backendStatusUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log('🔍 [STATUS] Backend response status:', statusResponse.status);

    if (!statusResponse.ok) {
      console.error(`❌ Backend status check failed: ${statusResponse.status}`);
      return NextResponse.json(
        { 
          success: false, 
          error: `Status check failed: ${statusResponse.status}` 
        },
        { status: statusResponse.status }
      );
    }

    const statusData = await statusResponse.json();
    
    console.log('🔍 [STATUS] Backend response:', JSON.stringify(statusData, null, 2));
    console.log('🔍 [STATUS] Status:', statusData?.data?.status);
    console.log('🔍 [STATUS] Content present:', !!statusData?.content || !!statusData?.data?.content);
    
    // Check for content in multiple possible locations
    const content = statusData?.content || statusData?.data?.content || statusData?.data?.generated_content;
    const status = statusData?.data?.status || statusData?.status;
    
    console.log('🔍 [STATUS] Extracted status:', status);
    console.log('🔍 [STATUS] Extracted content length:', content?.length || 0);
    
    // Transform response to match frontend expectations
    const transformedResponse = {
      ...statusData,
      status: status,
      content: content,
      content_found: !!content && status === 'completed'
    };
    
    console.log('🔍 [STATUS] Transformed response status:', transformedResponse.status);
    console.log('🔍 [STATUS] Transformed content_found:', transformedResponse.content_found);

    return NextResponse.json(transformedResponse);

  } catch (error) {
    console.error("❌ Status check error:", error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : "Unknown error" 
      },
      { status: 500 }
    );
  }
}