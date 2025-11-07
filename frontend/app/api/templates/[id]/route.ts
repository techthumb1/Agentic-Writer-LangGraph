import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }  // Changed to Promise
) {
  try {
    const { id } = await params;  // Await params
    console.log(`🔍 [TEMPLATE DETAIL] Fetching template: ${id}`);
    
    const response = await fetch(`${FASTAPI_BASE_URL}/api/templates/${id}`, {
      headers: {
        ...(FASTAPI_API_KEY && { 'Authorization': `Bearer ${FASTAPI_API_KEY}` }),
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`);
    }

    const data = await response.json();
    console.log(`✅ [TEMPLATE DETAIL] Got ${Object.keys(data.data?.parameters || {}).length} parameters`);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ [TEMPLATE DETAIL] Error:', error);
    return NextResponse.json({ error: 'Failed to fetch template' }, { status: 500 });
  }
}