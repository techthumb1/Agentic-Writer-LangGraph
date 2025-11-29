// File: frontend/app/api/analytics/performance/route.ts
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  const range = request.nextUrl.searchParams.get('range') || '30d';
  
  try {
    const response = await fetch(`${BACKEND_URL}/analytics/performance?range=${range}`);
    if (!response.ok) throw new Error(`Backend error: ${response.status}`);
    return NextResponse.json(await response.json());
  } catch (error) {
    console.error('Performance analytics fetch failed:', error);
    return NextResponse.json({ error: 'Performance unavailable' }, { status: 500 });
  }
}