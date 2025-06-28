// frontend/app/api/generate/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('Proxying generation request to FastAPI backend:', {
      template: body.template,
      style_profile: body.style_profile,
      parameters: Object.keys(body.dynamic_parameters || {})
    });

    // Send the payload as-is to backend - let backend handle file extensions
    const backendPayload = {
      template: body.template,  // Remove .yaml addition
      style_profile: body.style_profile,  // Remove .yaml addition
      dynamic_parameters: body.dynamic_parameters || {},
      priority: body.priority || 1,
      timeout_seconds: body.timeout_seconds || 300
    };

    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(backendPayload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch {
        errorData = { detail: errorText };
      }
      
      console.error('FastAPI backend error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorData
      });
      
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.detail || errorData.error?.message || 'Backend request failed',
          details: errorData
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('FastAPI backend response:', {
      success: data.success,
      request_id: data.data?.request_id,
      status: data.data?.status
    });

    return NextResponse.json({ 
      success: true, 
      data: data.data 
    });

  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      {
        success: false,
        error: {
          message: 'Proxy request failed',
          details: error instanceof Error ? error.message : 'Unknown proxy error',
        },
      },
      { status: 500 }
    );
  }
}

// Get generation status/result
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const requestId = searchParams.get('request_id');
    
    if (!requestId) {
      return NextResponse.json(
        { 
          success: false,
          error: 'request_id parameter required' 
        },
        { status: 400 }
      );
    }

    console.log('Checking generation status:', requestId);

    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/generate?request_id=${requestId}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.error('❌ Status check failed:', errorData);
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.detail || 'Failed to check generation status'
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ Status check response:', {
      request_id: requestId,
      status: data.data?.status,
      progress: data.data?.progress
    });

    return NextResponse.json({ 
      success: true, 
      data: data.data 
    });

  } catch (error) {
    console.error('🚨 Status check error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to check generation status' 
      },
      { status: 500 }
    );
  }
}

// Cancel generation
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const requestId = searchParams.get('request_id');
    
    if (!requestId) {
      return NextResponse.json(
        { 
          success: false,
          error: 'request_id parameter required' 
        },
        { status: 400 }
      );
    }

    console.log('📤 Cancelling generation:', requestId);

    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/generate?request_id=${requestId}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.detail || 'Failed to cancel generation'
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ Generation cancelled:', requestId);

    return NextResponse.json({ 
      success: true, 
      data: data.data 
    });

  } catch (error) {
    console.error('🚨 Cancellation error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to cancel generation' 
      },
      { status: 500 }
    );
  }
}