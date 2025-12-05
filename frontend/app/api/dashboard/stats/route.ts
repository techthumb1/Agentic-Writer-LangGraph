// File: frontend/app/api/dashboard/stats/route.ts
import { NextResponse } from 'next/server'
import { auth } from '@/auth'

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL

export async function GET() {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const response = await fetch(`${BACKEND_URL}/api/dashboard/stats`, {
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': session.user.id
      }
    })

    if (!response.ok) {
      throw new Error('Backend stats fetch failed')
    }

    const stats = await response.json()
    
    const result = NextResponse.json(stats)
    result.headers.set('Cache-Control', 'private, s-maxage=60, stale-while-revalidate=120')
    return result

  } catch (error) {
    console.error('❌ Dashboard stats error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch dashboard stats' },
      { status: 500 }
    )
  }
}