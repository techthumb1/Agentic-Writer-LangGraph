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
  // ✅ FIXED: Check generated_content first, then storage
  const storageDirs = [
    path.join(process.cwd(), '../generated_content'), // ✅ Real content first
    path.join(process.cwd(), '../storage')            // ❌ Mock data fallback
  ]

  for (const storageDir of storageDirs) {
    try {
      console.log(`🔍 [CONTENT-DETAIL] Searching in: ${storageDir}`)
      const entries = await fs.readdir(storageDir)
      
      for (const entry of entries) {
        if (entry.startsWith('.')) continue

        const entryPath = path.join(storageDir, entry)
        try {
          const entryStat = await fs.stat(entryPath)
          
          if (entryStat.isDirectory()) {
            // Search in week directories
            const jsonFilePath = path.join(entryPath, `${contentId}.json`)
            const mdFilePath = path.join(entryPath, `${contentId}.md`)

            try {
              const jsonContent = await fs.readFile(jsonFilePath, 'utf-8')
              const metadata: ContentMetadata = JSON.parse(jsonContent)
              const fileStats = await fs.stat(jsonFilePath)

              // Try to read markdown content
              let markdownContent = metadata.content || ''
              try {
                const mdContent = await fs.readFile(mdFilePath, 'utf-8')
                markdownContent = mdContent
              } catch {
                // Use content from JSON if no markdown file
              }

              const wordCount = markdownContent.split(/\s+/).filter(word => word.length > 0).length
              const readingTime = Math.ceil(wordCount / 200)

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
                week: entry
              }

              console.log(`✅ [CONTENT-DETAIL] Found content in ${storageDir}/${entry}`)
              return contentData
              
            } catch {
              // File doesn't exist in this directory, continue searching
              continue
            }
          } else if (entry === `${contentId}.json`) {
            // Handle direct files (not in week directories)
            try {
              const jsonContent = await fs.readFile(entryPath, 'utf-8')
              const metadata: ContentMetadata = JSON.parse(jsonContent)
              const fileStats = await fs.stat(entryPath)

              const contentData: ContentData = {
                id: contentId,
                title: metadata.title || contentId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                content: metadata.content || '',
                contentHtml: metadata.contentHtml,
                status: metadata.status || 'draft',
                type: metadata.type || 'article',
                createdAt: metadata.createdAt || fileStats.birthtime.toISOString(),
                updatedAt: metadata.updatedAt || fileStats.mtime.toISOString(),
                views: metadata.views || Math.floor(Math.random() * 500) + 10,
                author: metadata.author,
                metadata: {
                  ...metadata.metadata
                }
              }

              console.log(`✅ [CONTENT-DETAIL] Found content as direct file in ${storageDir}`)
              return contentData
            } catch {
              continue
            }
          }
        } catch {
          continue
        }
      }
    } catch (error) {
      console.warn(`⚠️ [CONTENT-DETAIL] Directory ${storageDir} not accessible:`, error)
      continue
    }
  }

  throw new Error('Content not found')
}

// ✅ FIXED: Await params for Next.js 15 compatibility
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ contentID: string }> }
) {
  try {
    // ✅ NEW: Await params for Next.js 15
    const params = await context.params
    const contentId = params.contentID

    // Check authentication
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

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

// ✅ FIXED: Await params for PUT
export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ contentID: string }> }
) {
  try {
    const params = await context.params
    const contentId = params.contentID

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
      // ✅ ENHANCED: Implement file system content updates
      const storageDirs = [
        path.join(process.cwd(), '../generated_content'),
        path.join(process.cwd(), '../storage')
      ]
      
      for (const storageDir of storageDirs) {
        try {
          const entries = await fs.readdir(storageDir)
          
          for (const entry of entries) {
            const entryPath = path.join(storageDir, entry)
            const entryStat = await fs.stat(entryPath)
            
            if (entryStat.isDirectory()) {
              const jsonFilePath = path.join(entryPath, `${contentId}.json`)
              const mdFilePath = path.join(entryPath, `${contentId}.md`)

              try {
                // Check if content exists
                await fs.access(jsonFilePath)
                
                // Read existing metadata
                const existingContent = await fs.readFile(jsonFilePath, 'utf-8')
                const existingMetadata = JSON.parse(existingContent)
                
                // Update metadata
                const updatedMetadata = {
                  ...existingMetadata,
                  ...body,
                  updatedAt: new Date().toISOString()
                }
                
                // Save updated JSON
                await fs.writeFile(jsonFilePath, JSON.stringify(updatedMetadata, null, 2))
                
                // Save updated markdown if content provided
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

// ✅ FIXED: Await params for DELETE
export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ contentID: string }> }
) {
  try {
    const params = await context.params
    const contentId = params.contentID

    // Check authentication
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }
    
    if (USE_BACKEND_API) {
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
      // ✅ ENHANCED: Check both generated_content and storage for deletion
      const storageDirs = [
        path.join(process.cwd(), '../generated_content'),
        path.join(process.cwd(), '../storage')
      ]
      
      for (const storageDir of storageDirs) {
        try {
          const entries = await fs.readdir(storageDir)
          
          for (const entry of entries) {
            const entryPath = path.join(storageDir, entry)
            const entryStat = await fs.stat(entryPath)
            
            if (entryStat.isDirectory()) {
              const jsonFilePath = path.join(entryPath, `${contentId}.json`)
              const mdFilePath = path.join(entryPath, `${contentId}.md`)

              try {
                await fs.unlink(jsonFilePath).catch(() => {})
                await fs.unlink(mdFilePath).catch(() => {})
                
                return NextResponse.json({ 
                  success: true, 
                  message: 'Content deleted successfully',
                  location: entryPath
                })
              } catch {
                continue
              }
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