// frontend/app/api/health/db/route.ts

import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma.node';

export async function GET() {
  try {
    const start = Date.now();
    await prisma.$queryRaw`SELECT 1`;
    const responseTime = Date.now() - start;

    const dbHealth = {
      status: 'healthy',
      database: 'postgresql',
      connection: 'active',
      response_time: `${responseTime}ms`,
      last_check: new Date().toISOString()
    };

    return NextResponse.json({
      success: true,
      health: dbHealth,
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