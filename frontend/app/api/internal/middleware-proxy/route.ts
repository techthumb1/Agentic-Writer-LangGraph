// frontend/app/api/internal/middleware-proxy/route.ts
import { NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function GET() {
  try {
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${backendUrl}/api/users/count`, {
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      }
    });
    
    const data = await response.json();
    return NextResponse.json({ ok: true, count: data.count || 0 });
  } catch {
    return NextResponse.json({ ok: false, count: 0 }, { status: 500 });
  }
}