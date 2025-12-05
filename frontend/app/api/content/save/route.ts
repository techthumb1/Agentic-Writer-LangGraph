// frontend/app/api/content/save/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL

function jsonError(message: string, status = 400) {
  return NextResponse.json({ error: message }, { status })
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) return jsonError('Unauthorized', 401)

    const body = await request.json()
    
    if (!body.content) {
      return jsonError('Content is required', 400)
    }

    const response = await fetch(`${BACKEND_URL}/api/content/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': session.user.id
      },
      body: JSON.stringify({
        userId: session.user.id,
        title: body.filename || body.title || `Generated Content ${new Date().toISOString().split('T')[0]}`,
        content: body.content,
        contentHtml: body.contentHtml || null,
        status: body.status || 'draft',
        type: body.type || 'article',
        metadata: body.metadata || {}
      })
    })

    if (!response.ok) {
      return jsonError('Failed to save content', response.status)
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    console.error('❌ [CONTENT-SAVE] Error:', error)
    return jsonError('Failed to save content', 500)
  }
}