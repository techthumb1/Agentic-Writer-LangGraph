// frontend/app/api/generate-content/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/auth';

export async function POST(request: NextRequest) {
  const session = await auth();
  
  if (!session?.user?.id) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { 
      template, 
      templateId,
      styleProfile, 
      styleProfileId,
      topic,
      audience,
      dynamic_parameters,
      parameters, 
    } = body;

    const finalTemplate = template || templateId;
    const finalStyleProfile = styleProfile || styleProfileId;

    if (!finalTemplate || !finalStyleProfile) {
      return NextResponse.json(
        { error: 'Template and Style Profile are required' },
        { status: 400 }
      );
    }

    // Forward to backend
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${backendUrl}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      },
      body: JSON.stringify({
        template_id: finalTemplate,
        style_profile: finalStyleProfile,
        topic: topic || dynamic_parameters?.topic || "Untitled",
        audience: audience || dynamic_parameters?.target_audience || "General audience",
        dynamic_parameters: dynamic_parameters || parameters || {},
        user_id: session.user.id
      })
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: 'Content generation failed', details: error },
        { status: response.status }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('Content generation API error:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${backendUrl}/api/content?action=${action || 'templates'}`, {
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      }
    });

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('API GET error:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}