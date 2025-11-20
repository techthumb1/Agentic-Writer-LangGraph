// frontend/app/api/content/save/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma.node'

function jsonError(message: string, status = 400, details?: unknown) {
  return NextResponse.json({ error: message, details }, { status })
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user) return jsonError('Unauthorized', 401)

    const body = await request.json()
    console.log('📥 [CONTENT-SAVE] Received body:', JSON.stringify(body, null, 2))
    
    // Validate required fields
    if (!body.content) {
      return jsonError('Content is required', 400)
    }

    const newContent = await prisma.content.create({
      data: {
        userId: session.user.id,
        title: body.filename || body.title || `Generated Content ${new Date().toISOString().split('T')[0]}`,
        content: body.content,
        contentHtml: body.contentHtml || null,
        status: body.status || 'draft',
        type: body.type || 'article',
        metadata: body.metadata || {},
      },
    })

    return NextResponse.json({
      success: true,
      contentId: newContent.id,
      message: 'Content saved successfully',
    })
  } catch (error) {
    console.error('❌ [CONTENT-SAVE] Error:', error)
    return jsonError(
      'Failed to save content',
      500,
      error instanceof Error ? error.message : 'Unknown error'
    )
  }
}