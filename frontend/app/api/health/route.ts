import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma.node'

export async function GET() {
  try {
    // Check database connection
    await prisma.$queryRaw`SELECT 1`
    
    return NextResponse.json({
      status: 'healthy',
      version: process.env.npm_package_version || '1.0.0',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      dependencies: {
        database: 'connected',
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
