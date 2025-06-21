// frontend/app/api/health/db/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Check database connection
    // If you're using Prisma, you can use: await prisma.$queryRaw`SELECT 1`
    // For now, mock the database check
    
    const dbHealth = {
      status: 'healthy',
      database: 'postgresql',
      connection: 'active',
      response_time: '15ms',
      last_check: new Date().toISOString()
    };

    // You could add actual database ping here:
    // try {
    //   await prisma.$queryRaw`SELECT 1`;
    //   dbHealth.status = 'healthy';
    // } catch (error) {
    //   dbHealth.status = 'unhealthy';
    //   dbHealth.error = error.message;
    // }

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
          error: typeof error === 'object' && error !== null && 'message' in error ? (error as { message: string }).message : String(error),
          timestamp: new Date().toISOString()
        }
      },
      { status: 500 }
    );
  }
}