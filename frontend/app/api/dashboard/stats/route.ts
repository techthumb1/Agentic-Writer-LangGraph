// frontend/app/api/dashboard/stats/route.ts
import { NextResponse } from 'next/server'
import { auth } from '@/app/api/auth/[...nextauth]/route'
import fs from 'fs/promises'
import path from 'path'

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

interface ContentMetadata {
  title: string
  status: 'published' | 'draft'
  updatedAt?: string
  createdAt?: string
  type?: string
  views?: number
}

// Environment configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'
const USE_BACKEND_API = process.env.USE_BACKEND_API === 'true'

// Backend response interfaces

interface BackendActivityResponse {
  activities: ActivityItem[]
}

interface ContentItem {
  id: string
  title: string
  status: 'published' | 'draft'
  updatedAt: string
  createdAt: string
  type: string
  views?: number
}

async function fetchFromBackend(endpoint: string): Promise<DashboardStats> {
  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      // Add timeout
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`Failed to fetch from backend ${endpoint}:`, error)
    throw error
  }
}

async function getStatsFromFileSystem(): Promise<DashboardStats> {
  const storageDir = path.join(process.cwd(), '../storage')
  const stats: DashboardStats = {
    totalContent: 0,
    drafts: 0,
    published: 0,
    views: 0,
    recentContent: [],
    recentActivity: []
  }

  try {
    const weeks = await fs.readdir(storageDir)
    const contentItems: Array<RecentContentItem & { createdAt: Date }> = []

    for (const week of weeks) {
      if (week.startsWith('.')) continue

      const weekDir = path.join(storageDir, week)
      try {
        const weekStat = await fs.stat(weekDir)
        if (!weekStat.isDirectory()) continue

        const files = await fs.readdir(weekDir)
        
        for (const file of files) {
          if (file.endsWith('.json')) {
            try {
              const filePath = path.join(weekDir, file)
              const content = await fs.readFile(filePath, 'utf-8')
              const metadata: ContentMetadata = JSON.parse(content)

              const slug = file.replace(/\.json$/, '')
              const fileStats = await fs.stat(filePath)
              
              contentItems.push({
                id: slug,
                title: metadata.title || slug.replace(/_/g, ' '),
                status: metadata.status || 'draft',
                updatedAt: metadata.updatedAt || fileStats.mtime.toISOString(),
                type: metadata.type || 'article',
                createdAt: new Date(metadata.createdAt || fileStats.birthtime)
              })

              // Count stats
              stats.totalContent++
              if (metadata.status === 'published') {
                stats.published++
              } else {
                stats.drafts++
              }
              
              // Add to views (mock data or from metadata)
              stats.views += metadata.views || Math.floor(Math.random() * 100)

            } catch (error) {
              console.error(`Error processing file ${file}:`, error)
            }
          }
        }
      } catch (error) {
        console.error(`Error processing week ${week}:`, error)
      }
    }

    // Sort by creation date and get recent content
    contentItems.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
    stats.recentContent = contentItems.slice(0, 4).map(item => ({
      id: item.id,
      title: item.title,
      status: item.status,
      updatedAt: item.updatedAt,
      type: item.type
    }))

    // Generate recent activity from content
    stats.recentActivity = contentItems.slice(0, 4).map(item => ({
      id: `activity-${item.id}`,
      type: item.status === 'published' ? 'published' : 'created' as const,
      description: `${item.status === 'published' ? 'Published' : 'Created'} "${item.title}"`,
      timestamp: item.updatedAt
    }))

  } catch (error) {
    console.error('Error reading from file system:', error)
  }

  return stats
}

interface BackendContentResponse {
  content: ContentItem[]
  totalViews: number
  views?: number  // Add this to handle both formats
  stats: {
    total: number
    published: number
    drafts: number
    types: number
  }
}

async function getStatsFromBackend(): Promise<DashboardStats> {
  try {
    // Try to get comprehensive stats from a single endpoint
    try {
      const stats = await fetchFromBackend('/api/dashboard/stats')
      return stats
    } catch (statsError) {
      console.log('Comprehensive stats endpoint not available, fetching individual endpoints...')
      console.error('Stats error:', statsError)
    }

    // Fallback: fetch from individual endpoints
    const [contentResponse, activityResponse] = await Promise.allSettled([
      fetch(`${BACKEND_URL}/api/content`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(5000),
      }).then(res => {
        if (!res.ok) throw new Error(`Backend API error: ${res.status}`)
        return res.json() as Promise<BackendContentResponse>
      }),
      fetch(`${BACKEND_URL}/api/dashboard/activity`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(5000),
      }).then(res => {
        if (!res.ok) throw new Error(`Backend API error: ${res.status}`)
        return res.json() as Promise<BackendActivityResponse>
      })
    ])

    const contentData: BackendContentResponse | null = contentResponse.status === 'fulfilled' ? contentResponse.value : null
    const activityData: BackendActivityResponse | null = activityResponse.status === 'fulfilled' ? activityResponse.value : null

    // Build stats from available data
    const stats: DashboardStats = {
      totalContent: 0,
      drafts: 0,
      published: 0,
      views: 0,
      recentContent: [],
      recentActivity: []
    }

    if (contentData?.content && Array.isArray(contentData.content)) {
      stats.totalContent = contentData.content.length
      stats.drafts = contentData.content.filter((item: ContentItem) => item.status === 'draft').length
      stats.published = contentData.content.filter((item: ContentItem) => item.status === 'published').length
      stats.views = contentData.totalViews || 0
      stats.recentContent = contentData.content.slice(0, 4).map((item: ContentItem) => ({
        id: item.id || item.title.toLowerCase().replace(/\s+/g, '-'),
        title: item.title,
        status: item.status || 'draft',
        updatedAt: item.updatedAt || item.createdAt || new Date().toISOString(),
        type: item.type || 'article'
      }))
    }

    if (activityData?.activities && Array.isArray(activityData.activities)) {
      stats.recentActivity = activityData.activities.slice(0, 4)
    }

    return stats

  } catch (backendError) {
    console.error('Error fetching from backend APIs:', backendError)
    throw backendError
  }
}

export async function GET() {
  try {
    // Check authentication
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    let stats: DashboardStats

    if (USE_BACKEND_API) {
      console.log('🔄 Fetching dashboard stats from backend API...')
      try {
        stats = await getStatsFromBackend()
        console.log('✅ Successfully fetched stats from backend')
      } catch (backendError) {
        console.log('❌ Backend API failed, falling back to file system...')
        console.error('Backend error:', backendError)
        stats = await getStatsFromFileSystem()
      }
    } else {
      console.log('📁 Fetching dashboard stats from file system...')
      stats = await getStatsFromFileSystem()
    }

    // Add cache headers for better performance
    const response = NextResponse.json(stats)
    response.headers.set('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=120')
    
    return response

  } catch (error) {
    console.error('Dashboard stats API error:', error)
    
    // Return minimal fallback data instead of error
    const fallbackStats: DashboardStats = {
      totalContent: 0,
      drafts: 0,
      published: 0,
      views: 0,
      recentContent: [],
      recentActivity: []
    }

    return NextResponse.json(fallbackStats, { status: 200 })
  }
}

// Health check endpoint
export async function HEAD() {
  return new NextResponse(null, { status: 200 })
}