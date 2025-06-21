// frontend/app/api/generate/status/[requestId]/route.ts

import { NextRequest, NextResponse } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: { requestId: string } }
) {
  try {
    const { requestId } = params;
    
    console.log(`🔍 Checking status for request: ${requestId}`);

    // Forward the status check to your backend
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const statusResponse = await fetch(`${backendUrl}/status/${requestId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

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
    console.log(`📊 Backend status response:`, statusData);

    return NextResponse.json(statusData);

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