// frontend/app/content/%5BcontentID%5D/track-view/route.ts

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ contentID: string }> }
) {
  const { contentID } = await params;
  const body = await request.json();
  
  try {
    const response = await fetch(
      `${BACKEND_URL}/api/content/${contentID}/track-view`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }
    );
    
    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json({ views: 0, unique_views: 0 });
  }
}