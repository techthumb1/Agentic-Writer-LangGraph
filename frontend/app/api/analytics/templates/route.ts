// File: frontend/app/api/analytics/templates/route.ts
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  const range = request.nextUrl.searchParams.get('range') || '30d';
  
  try {
    const response = await fetch(`${BACKEND_URL}/analytics/templates?range=${range}`);
    if (!response.ok) throw new Error(`Backend error: ${response.status}`);
    return NextResponse.json(await response.json());
  } catch (error) {
    console.error('Template analytics fetch failed:', error);
    return NextResponse.json({ error: 'Templates unavailable' }, { status: 500 });
  }
}