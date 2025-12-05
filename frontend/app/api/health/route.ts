import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check backend health
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${backendUrl}/health`, {
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      }
    });

    const backendHealth = await response.json();
    
    return NextResponse.json({
      status: response.ok ? 'healthy' : 'degraded',
      version: process.env.npm_package_version || '1.0.0',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      dependencies: {
        backend: response.ok ? 'connected' : 'unavailable',
        database: backendHealth.services?.database?.status || 'unknown',
        nextjs: 'running',
      },
    })
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        message: 'Health check failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}