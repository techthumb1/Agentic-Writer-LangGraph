// frontend/app/api/content/[contentID]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import fs from 'fs/promises'
import path from 'path'

interface ContentData {
  id: string
  title: string
  content: string
  contentHtml?: string
  status: 'draft' | 'published'
  type: string
  createdAt: string
  updatedAt: string
  views?: number
  author?: string
  metadata?: {
    template?: string
    styleProfile?: string
    wordCount?: number
    readingTime?: number
    [key: string]: unknown
  }
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
  contentHtml?: string
  author?: string
  metadata?: Record<string, unknown>
}

// Environment configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'
const USE_BACKEND_API = process.env.USE_BACKEND_API === 'true'

async function fetchFromBackend(contentId: string): Promise<ContentData> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/content/${contentId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Content not found')
      }
      throw new Error(`Backend API error: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Failed to fetch from backend:', error)
    throw error
  }
}

async function getContentFromFileSystem(contentId: string): Promise<ContentData> {
  // Check both storage and generated_content directories
  const storageDirs = [
    path.join(process.cwd(), '../storage'),
    path.join(process.cwd(), '../generated_content')
  ]

  for (const storageDir of storageDirs) {
    try {
      const weeks = await fs.readdir(storageDir)
      
      for (const week of weeks) {
        if (week.startsWith('.')) continue

        const weekDir = path.join(storageDir, week)
        try {
          const weekStat = await fs.stat(weekDir)
          if (!weekStat.isDirectory()) continue

          const jsonFilePath = path.join(weekDir, `${contentId}.json`)
          const mdFilePath = path.join(weekDir, `${contentId}.md`)

          try {
            // Try to read JSON metadata file
            const jsonContent = await fs.readFile(jsonFilePath, 'utf-8')
            const metadata: ContentMetadata = JSON.parse(jsonContent)
            const fileStats = await fs.stat(jsonFilePath)

            // Try to read markdown content file if it exists
            let markdownContent = metadata.content || ''
            try {
              const mdContent = await fs.readFile(mdFilePath, 'utf-8')
              markdownContent = mdContent
            } catch {
              // Markdown file doesn't exist, use content from JSON
            }

            // Calculate word count and reading time
            const wordCount = markdownContent.split(/\s+/).filter(word => word.length > 0).length
            const readingTime = Math.ceil(wordCount / 200) // Average reading speed

            const contentData: ContentData = {
              id: contentId,
              title: metadata.title || contentId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
              content: markdownContent,
              contentHtml: metadata.contentHtml,
              status: metadata.status || 'draft',
              type: metadata.type || 'article',
              createdAt: metadata.createdAt || fileStats.birthtime.toISOString(),
              updatedAt: metadata.updatedAt || fileStats.mtime.toISOString(),
              views: metadata.views || Math.floor(Math.random() * 500) + 10,
              author: metadata.author,
              metadata: {
                template: metadata.metadata?.template as string | undefined,
                styleProfile: typeof metadata.metadata?.styleProfile === 'string' ? metadata.metadata?.styleProfile : undefined,
                wordCount,
                readingTime,
                ...metadata.metadata
              },
              week
            }

            return contentData
            
          } catch {
            // File doesn't exist in this week, continue searching
            continue
          }
        } catch {
          continue
        }
      }
    } catch {
      // Directory doesn't exist or can't be accessed, try next one
      continue
    }
  }

  // Content not found in any directory
  throw new Error('Content not found')
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ contentID: string }> }
) {
  try {
    // Check authentication
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // ✅ FIX: Await params for Next.js 15 compatibility
    const resolvedParams = await params
    const contentId = resolvedParams.contentID

    if (!contentId) {
      return NextResponse.json(
        { error: 'Content ID is required' },
        { status: 400 }
      )
    }

    let contentData: ContentData

    if (USE_BACKEND_API) {
      console.log(`🔄 Fetching content ${contentId} from backend API...`)
      try {
        contentData = await fetchFromBackend(contentId)
        console.log(`✅ Successfully fetched content from backend`)
      } catch {
        console.log('❌ Backend API failed, falling back to file system...')
        contentData = await getContentFromFileSystem(contentId)
      }
    } else {
      console.log(`📁 Fetching content ${contentId} from file system...`)
      contentData = await getContentFromFileSystem(contentId)
    }

    // Add cache headers
    const response = NextResponse.json(contentData)
    response.headers.set('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=120')
    
    return response

  } catch (error) {
    console.error('Content detail API error:', error)
    
    if (error instanceof Error && error.message === 'Content not found') {
      return NextResponse.json(
        { error: 'Content not found' },
        { status: 404 }
      )
    }
    
    return NextResponse.json(
      { 
        error: 'Failed to fetch content',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// PUT endpoint for updating content
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ contentID: string }> }
) {
  try {
    // Check authentication
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // ✅ FIX: Await params for Next.js 15 compatibility
    const resolvedParams = await params
    const contentId = resolvedParams.contentID
    const body = await request.json()
    
    if (USE_BACKEND_API) {
      // Forward to backend API
      const response = await fetch(`${BACKEND_URL}/api/content/${contentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        if (response.status === 404) {
          return NextResponse.json(
            { error: 'Content not found' },
            { status: 404 }
          )
        }
        throw new Error(`Backend API error: ${response.status}`)
      }

      const data = await response.json()
      return NextResponse.json(data)
    } else {
      // ✅ ENHANCEMENT: Implement file system content updates
      try {
        const storageDirs = [
          path.join(process.cwd(), '../storage'),
          path.join(process.cwd(), '../generated_content')
        ]

        for (const storageDir of storageDirs) {
          try {
            const weeks = await fs.readdir(storageDir)
            
            for (const week of weeks) {
              if (week.startsWith('.')) continue

              const weekDir = path.join(storageDir, week)
              const jsonFilePath = path.join(weekDir, `${contentId}.json`)
              const mdFilePath = path.join(weekDir, `${contentId}.md`)

              try {
                // Check if file exists
                await fs.access(jsonFilePath)
                
                // Update JSON metadata
                const updatedMetadata = {
                  ...body,
                  updatedAt: new Date().toISOString()
                }
                
                await fs.writeFile(jsonFilePath, JSON.stringify(updatedMetadata, null, 2))
                
                // Update markdown content if provided
                if (body.content) {
                  await fs.writeFile(mdFilePath, body.content)
                }
                
                return NextResponse.json({ 
                  success: true, 
                  message: 'Content updated successfully',
                  contentId,
                  updatedAt: updatedMetadata.updatedAt
                })
                
              } catch {
                continue
              }
            }
          } catch {
            continue
          }
        }
        
        return NextResponse.json(
          { error: 'Content not found for update' },
          { status: 404 }
        )
      } catch (error) {
        console.error('File system update error:', error)
        return NextResponse.json(
          { error: 'Failed to update content in file system' },
          { status: 500 }
        )
      }
    }

  } catch (error) {
    console.error('Content update error:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to update content',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// DELETE endpoint for deleting content
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ contentID: string }> }
) {
  try {
    // Check authentication
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // ✅ FIX: Await params for Next.js 15 compatibility
    const resolvedParams = await params
    const contentId = resolvedParams.contentID
    
    if (USE_BACKEND_API) {
      // Forward to backend API
      const response = await fetch(`${BACKEND_URL}/api/content/${contentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        if (response.status === 404) {
          return NextResponse.json(
            { error: 'Content not found' },
            { status: 404 }
          )
        }
        throw new Error(`Backend API error: ${response.status}`)
      }

      const data = await response.json()
      return NextResponse.json(data)
    } else {
      // Handle content deletion in file system
      const storageDirs = [
        path.join(process.cwd(), '../storage'),
        path.join(process.cwd(), '../generated_content')
      ]

      for (const storageDir of storageDirs) {
        try {
          const weeks = await fs.readdir(storageDir)
          
          for (const week of weeks) {
            if (week.startsWith('.')) continue

            const weekDir = path.join(storageDir, week)
            const jsonFilePath = path.join(weekDir, `${contentId}.json`)
            const mdFilePath = path.join(weekDir, `${contentId}.md`)

            try {
              // Try to delete both files
              await fs.unlink(jsonFilePath).catch(() => {})
              await fs.unlink(mdFilePath).catch(() => {})
              
              return NextResponse.json({ 
                success: true, 
                message: 'Content deleted successfully',
                contentId 
              })
            } catch {
              continue
            }
          }
        } catch {
          continue
        }
      }

      return NextResponse.json(
        { error: 'Content not found' },
        { status: 404 }
      )
    }

  } catch (error) {
    console.error('Content deletion error:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to delete content',
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