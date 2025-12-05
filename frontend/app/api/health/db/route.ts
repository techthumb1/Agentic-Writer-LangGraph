// frontend/app/api/health/db/route.ts

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;
    const start = Date.now();
    
    const response = await fetch(`${backendUrl}/health`, {
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      }
    });
    
    const responseTime = Date.now() - start;
    const data = await response.json();

    return NextResponse.json({
      success: true,
      health: {
        status: data.services?.database?.status || 'unknown',
        database: 'postgresql',
        connection: response.ok ? 'active' : 'failed',
        response_time: `${responseTime}ms`,
        backend_latency: `${data.services?.database?.latency_ms || 0}ms`,
        last_check: new Date().toISOString()
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Database health check error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Database health check failed',
        health: {
          status: 'unhealthy',
          error: error instanceof Error ? error.message : String(error),
          timestamp: new Date().toISOString()
        }
      },
      { status: 503 }
    );
  }
}