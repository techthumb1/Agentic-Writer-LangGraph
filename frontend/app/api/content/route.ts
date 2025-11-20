// frontend/app/api/content/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma.node'
import { JsonValue } from '@prisma/client/runtime/library'

// Type definitions
interface PrismaContent {
  id: string
  title: string
  content: string
  contentHtml: string | null
  status: string
  type: string
  views: number | bigint
  userId: string
  createdAt: Date
  updatedAt: Date
  metadata: JsonValue
}

interface ContentRequestBody {
  userId?: string
  title?: string
  content?: string
  contentHtml?: string
  status?: 'draft' | 'published' | 'completed'
  type?: string
  metadata?: Record<string, unknown>
}

// Small helper
function jsonError(message: string, status = 400, details?: unknown) {
  return NextResponse.json({ error: message, details }, { status })
}

/**
 * GET /api/content
 * Returns the authenticated user's content list + simple stats.
 */
export async function GET() {
  try {
    const session = await auth()
    if (!session?.user) return jsonError('Unauthorized', 401)

    const content = await prisma.content.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' },
    })

    const totalViews = content.reduce((sum: number, c: PrismaContent) => sum + (Number(c.views) || 0), 0)
    const uniqueTypes = new Set(content.map((c: PrismaContent) => c.type)).size

    const response = {
      content: content.map((c: PrismaContent) => ({
        id: c.id,
        title: c.title,
        date: c.createdAt?.toISOString?.() ?? new Date(c.createdAt).toISOString(),
        status: c.status as 'draft' | 'published' | 'completed',
        type: c.type,
        template_type: c.type,
        views: Number(c.views) || 0,
        updatedAt: c.updatedAt?.toISOString?.() ?? new Date(c.updatedAt).toISOString(),
        createdAt: c.createdAt?.toISOString?.() ?? new Date(c.createdAt).toISOString(),
        metadata: c.metadata as Record<string, unknown>,
      })),
      total_views: totalViews,
      stats: {
        total: content.length,
        published: content.filter((c: PrismaContent) => c.status === 'published').length,
        drafts: content.filter((c: PrismaContent) => c.status === 'draft').length,
        types: uniqueTypes,
      },
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error('❌ [CONTENT-API][GET] Error:', error)
    return jsonError('Failed to fetch content', 500, error instanceof Error ? error.message : 'Unknown error')
  }
}

/**
 * POST /api/content
 * Two paths:
 * 1) Internal service-to-service write with API key header (bypass NextAuth):
 *    Header: x-writerzroom-key: <LANGGRAPH_API_KEY>
 * 2) Authenticated user write (requires session).
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({} as ContentRequestBody))

    // ---- Path 1: Internal API-key bypass (FastAPI -> Next.js) ----
    const incomingKey = request.headers.get('x-writerzroom-key')
    const serverKey = process.env.LANGGRAPH_API_KEY

    if (incomingKey && serverKey && incomingKey === serverKey) {
      // Choose a userId to satisfy FK constraints:
      // - Prefer body.userId if provided
      // - Else use SERVICE_USER_ID env (set this to a valid user id)
      const serviceUserId = body.userId || process.env.SERVICE_USER_ID
      if (!serviceUserId) {
        return jsonError(
          'SERVICE_USER_ID missing. Set SERVICE_USER_ID env or include userId in payload when using API key bypass.',
          400
        )
      }

      const newContent = await prisma.content.create({
        data: {
          userId: serviceUserId,
          title: body.title || 'Untitled',
          content: body.content || '',
          contentHtml: body.contentHtml || '',
          status: body.status || 'completed', // backend sends 'completed'; defaults to 'completed' here
          type: body.type || 'article',
          metadata: body.metadata || {},
        },
      })

      return NextResponse.json({
        success: true,
        contentId: newContent.id,
        message: 'Content created via internal API key',
      })
    }

    // ---- Path 2: Standard authenticated user write ----
    const session = await auth()
    if (!session?.user) return jsonError('Unauthorized', 401)

    const newContent = await prisma.content.create({
      data: {
        userId: session.user.id,
        title: body.title || 'Untitled',
        content: body.content || '',
        contentHtml: body.contentHtml || '',
        status: body.status || 'draft',
        type: body.type || 'article',
        metadata: body.metadata || {},
      },
    })

    return NextResponse.json({
      success: true,
      contentId: newContent.id,
      message: 'Content created successfully',
    })
  } catch (error) {
    console.error('❌ [CONTENT-API][POST] Error:', error)
    return jsonError('Failed to create content', 500, error instanceof Error ? error.message : 'Unknown error')
  }
}

/**
 * HEAD /api/content
 */
export async function HEAD() {
  return new NextResponse(null, { status: 200 })
}