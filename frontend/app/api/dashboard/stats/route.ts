// File: frontend/app/api/dashboard/stats/route.ts
import { NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma.node'

export async function GET() {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const userId = session.user.id
    console.log(`📊 Fetching dashboard stats for user: ${userId}`)

    // Fetch ONLY this user's content
    const content = await prisma.content.findMany({
      where: { userId },
      orderBy: { updatedAt: 'desc' },
    })

    const totalContent = content.length
    const drafts = content.filter(c => c.status === 'draft').length
    const published = content.filter(c => c.status === 'published').length
    const totalViews = content.reduce((sum, c) => sum + Number(c.views || 0), 0)

    const recentContent = content.slice(0, 5).map(c => ({
      id: c.id,
      title: c.title,
      status: c.status as 'draft' | 'published',
      updated_at: c.updatedAt.toISOString(),
      type: c.type,
    }))

    const recentActivity = content.slice(0, 5).map(c => ({
      id: c.id,
      type: (c.status === 'published' ? 'published' : 'updated') as 'published' | 'updated',
      description: `${c.status === 'published' ? 'Published' : 'Updated'} "${c.title}"`,
      timestamp: c.updatedAt.toISOString(),
    }))

    const stats = {
      total_content: totalContent,
      drafts,
      published,
      views: totalViews,
      recent_content: recentContent,
      recent_activity: recentActivity,
    }

    console.log('✅ Successfully fetched stats from database')

    const response = NextResponse.json(stats)
    response.headers.set('Cache-Control', 'private, s-maxage=60, stale-while-revalidate=120')
    
    return response
  } catch (error) {
    console.error('❌ Dashboard stats error:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch dashboard stats',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}