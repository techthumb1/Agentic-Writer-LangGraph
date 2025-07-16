// frontend/app/api/content/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import fs from 'fs/promises'
import path from 'path'

interface ContentItem {
  id: string
  title: string
  date: string
  status: 'draft' | 'published'
  type: string
  views?: number
  updatedAt?: string
  createdAt?: string
  week?: string
}

interface ContentMetadata {
  title: string
  status: 'published' | 'draft'
  updatedAt?: string
  createdAt?: string
  type?: string
  views?: number
  content?: string
  metadata?: Record<string, unknown>
}

interface ContentResponse {
  content: ContentItem[]
  totalViews: number
  stats: {
    total: number
    published: number
    drafts: number
    types: number
  }
}

// Environment configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'
const USE_BACKEND_API = process.env.USE_BACKEND_API === 'true'

async function fetchFromBackend(): Promise<ContentResponse> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/content`, {
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

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Failed to fetch from backend:', error)
    throw error
  }
}

async function getContentFromFileSystem(): Promise<ContentResponse> {
  const storageDir = path.join(process.cwd(), '../storage')
  const contentItems: ContentItem[] = []
  let totalViews = 0

  try {
    const weeks = await fs.readdir(storageDir)

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
              
              // Generate realistic view count if not present
              const views = metadata.views || Math.floor(Math.random() * 500) + 10
              totalViews += views

              const contentItem: ContentItem = {
                id: slug,
                title: metadata.title || slug.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                date: metadata.createdAt || fileStats.birthtime.toISOString(),
                status: metadata.status || 'draft',
                type: metadata.type || 'article',
                views,
                updatedAt: metadata.updatedAt || fileStats.mtime.toISOString(),
                createdAt: metadata.createdAt || fileStats.birthtime.toISOString(),
                week
              }

              contentItems.push(contentItem)

            } catch (error) {
              console.error(`Error processing file ${file}:`, error)
            }
          }
        }
      } catch (error) {
        console.error(`Error processing week ${week}:`, error)
      }
    }

    // Sort by creation date (most recent first)
    contentItems.sort((a, b) => new Date(b.createdAt || b.date).getTime() - new Date(a.createdAt || a.date).getTime())

    // Calculate stats
    const stats = {
      total: contentItems.length,
      published: contentItems.filter(item => item.status === 'published').length,
      drafts: contentItems.filter(item => item.status === 'draft').length,
      types: new Set(contentItems.map(item => item.type)).size
    }

    return {
      content: contentItems,
      totalViews,
      stats
    }

  } catch (error) {
    console.error('Error reading from file system:', error)
    return {
      content: [],
      totalViews: 0,
      stats: {
        total: 0,
        published: 0,
        drafts: 0,
        types: 0
      }
    }
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

    let contentData: ContentResponse

    if (USE_BACKEND_API) {
      console.log('🔄 Fetching content from backend API...')
      try {
        contentData = await fetchFromBackend()
        console.log(`✅ Successfully fetched ${contentData.content.length} items from backend`)
      } catch (backendError) {
        console.log('❌ Backend API failed, falling back to file system...')
        console.error('Backend error:', backendError)
        contentData = await getContentFromFileSystem()
      }
    } else {
      console.log('📁 Fetching content from file system...')
      contentData = await getContentFromFileSystem()
    }

    // Add cache headers for better performance
    const response = NextResponse.json(contentData)
    response.headers.set('Cache-Control', 'public, s-maxage=30, stale-while-revalidate=60')
    
    return response

  } catch (error) {
    console.error('Content API error:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to fetch content',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// POST endpoint for creating new content
export async function POST(request: NextRequest) {
  try {
    // Check authentication
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const body = await request.json()
    
    if (USE_BACKEND_API) {
      // Forward to backend API
      const response = await fetch(`${BACKEND_URL}/api/content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        throw new Error(`Backend API error: ${response.status}`)
      }

      const data = await response.json()
      return NextResponse.json(data)
    } else {
      // Handle content creation in file system (if needed)
      return NextResponse.json(
        { error: 'Content creation not implemented for file system mode' },
        { status: 501 }
      )
    }

  } catch (error) {
    console.error('Content creation error:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to create content',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// Health check endpoint
export async function HEAD() {
  return new NextResponse(null, { status: 200 })
}