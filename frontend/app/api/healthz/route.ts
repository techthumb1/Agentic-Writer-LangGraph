// frontend/app/api/readyz/route.ts

import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma.node';

export async function GET() {
  const checks = {
    backend: false,
    database: false,
    overall: false,
  };

  try {
    // Check database
    await prisma.$queryRaw`SELECT 1`;
    checks.database = true;

    // Check backend connectivity (langgraph_app)
    const backendUrl = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    checks.backend = response.ok;

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