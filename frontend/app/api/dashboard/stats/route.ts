// File: frontend/app/api/dashboard/stats/route.ts
import { NextResponse } from 'next/server'
import { auth } from '@/app/api/auth/[...nextauth]/route'

interface DashboardStats {
  totalContent: number
  drafts: number
  published: number
  views: number
  recentContent: RecentContentItem[]
  recentActivity: ActivityItem[]
}

interface RecentContentItem {
  id: string
  title: string
  status: 'published' | 'draft'
  updatedAt: string
  type: string
}

interface ActivityItem {
  id: string
  type: 'published' | 'created' | 'updated' | 'generated'
  description: string
  timestamp: string
}

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

async function getStatsFromBackend(): Promise<DashboardStats> {
  const response = await fetch(`${BACKEND_URL}/api/dashboard/stats`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`Backend API error: ${response.status}`)
  }

  return await response.json()
}

export async function GET() {
  const session = await auth()
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    console.log('📊 Fetching dashboard stats from backend API...')
    const stats = await getStatsFromBackend()
    console.log('✅ Successfully fetched stats from backend')

    const response = NextResponse.json(stats)
    response.headers.set('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=120')
    
    return response
  } catch (error) {
    console.error('Dashboard stats API error:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch dashboard stats',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}