// frontend/app/api/style-profiles/route.ts
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY || 'your-api-key-here';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = searchParams.get('page') || '1';
    const limit = searchParams.get('limit') || '100';
    const search = searchParams.get('search') || '';
    const category = searchParams.get('category') || '';

    // Build query parameters
    const queryParams = new URLSearchParams({
      page,
      limit,
      search,
      category
    });

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/style-profiles?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.error('FastAPI error:', errorData);
      
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.detail || 'Failed to fetch style profiles',
          status: response.status 
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    console.log(`✅ Style profiles fetched successfully: ${data.data?.items?.length || 0} items`);
    
    return NextResponse.json({
  style_profiles: data.data.items,
  total: data.data.pagination.total
});

  } catch (error) {
    console.error('Frontend API error:', error);
    
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Internal server error',
        details: 'Failed to connect to FastAPI backend'
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward POST request to FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/style-profiles`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      return NextResponse.json(
        { success: false, error: errorData.detail || 'Failed to create style profile' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({
  style_profiles: data.data.items,
  total: data.data.pagination.total
});

  } catch (error) {
    console.error('Style profile creation error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create style profile' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { success: false, error: 'Style profile ID is required' },
        { status: 400 }
      );
    }

    // Forward PUT request to FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/style-profiles/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      return NextResponse.json(
        { success: false, error: errorData.detail || 'Failed to update style profile' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({
  style_profiles: data.data.items,
  total: data.data.pagination.total
});

  } catch (error) {
    console.error('Style profile update error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to update style profile' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { success: false, error: 'Style profile ID is required' },
        { status: 400 }
      );
    }

    // Forward DELETE request to FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/style-profiles/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      return NextResponse.json(
        { success: false, error: errorData.detail || 'Failed to delete style profile' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({
  style_profiles: data.data.items,
  total: data.data.pagination.total
});

  } catch (error) {
    console.error('Style profile deletion error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to delete style profile' },
      { status: 500 }
    );
  }
}