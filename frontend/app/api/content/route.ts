// frontend/app/api/content/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma.node'
import { JsonValue } from '@prisma/client/runtime/library'

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

function jsonError(message: string, status = 400, details?: unknown) {
  return NextResponse.json({ error: message, details }, { status })
}

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

    return NextResponse.json({
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
    })
  } catch (error) {
    console.error('❌ [CONTENT-API][GET] Error:', error)
    return jsonError('Failed to fetch content', 500, error instanceof Error ? error.message : 'Unknown error')
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({} as ContentRequestBody))

    // Internal API key bypass (backend -> frontend)
    const incomingKey = request.headers.get('x-writerzroom-key')
    const serverKey = process.env.LANGGRAPH_API_KEY

    if (incomingKey && serverKey && incomingKey === serverKey) {
      const userId = body.userId || process.env.SERVICE_USER_ID;

      if (!userId) {
        return jsonError('userId required for API key bypass', 400)
      }
    
      // Verify user exists
      const user = await prisma.user.findUnique({
        where: { id: userId }
      })

      if (!user) {
        return jsonError('User not found', 404)
      }

      const newContent = await prisma.content.create({
        data: {
          userId: userId,
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
        message: 'Content created via API key',
      })
    }

    // Authenticated user path
    const session = await auth()
    if (!session?.user) return jsonError('Unauthorized', 401)

    // Find existing user by email (may have different ID)
    const existingUser = await prisma.user.findUnique({
      where: { email: session.user.email! }
    })

    const userId = existingUser?.id || session.user.id

    if (!userId) {
      return jsonError('User ID required', 400);
    }

    if (!existingUser) {
      await prisma.user.create({
        data: {
          id: session.user.id,
          email: session.user.email!,
          name: session.user.name,
          image: session.user.image,
        },
      })
    }

    if (!userId) {
      return jsonError('User ID required', 400);
    }

    const newContent = await prisma.content.create({
      data: {
        userId: userId,
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

export async function HEAD() {
  return new NextResponse(null, { status: 200 })
}