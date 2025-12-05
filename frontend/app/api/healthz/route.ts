// frontend/app/api/readyz/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const checks = {
    backend: false,
    database: false,
    overall: false,
  };

  try {
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${backendUrl}/health`, {
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      },
      signal: AbortSignal.timeout(5000),
    });
    
    checks.backend = response.ok;
    
    if (response.ok) {
      const health = await response.json();
      checks.database = health.services?.database?.status === 'healthy';
    }

    checks.overall = checks.backend && checks.database;

    return NextResponse.json(checks, {
      status: checks.overall ? 200 : 503,
    });
  } catch {
    return NextResponse.json(
      { ...checks, error: 'Service unavailable' },
      { status: 503 }
    );
  }
}