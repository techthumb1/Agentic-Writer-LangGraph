// frontend/app/api/content/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL

function jsonError(message: string, status = 400) {
  return NextResponse.json({ error: message }, { status })
}

export async function GET() {
  try {
    const session = await auth()
    if (!session?.user) return jsonError('Unauthorized', 401)

    const response = await fetch(`${BACKEND_URL}/api/content`, {
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': session.user.id!
      }
    })

    if (!response.ok) {
      return jsonError('Failed to fetch content', response.status)
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    console.error('❌ [CONTENT-API][GET] Error:', error)
    return jsonError('Failed to fetch content', 500)
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}))
    
    // Check API key bypass
    const incomingKey = request.headers.get('x-writerzroom-key')
    const serverKey = process.env.LANGGRAPH_API_KEY

    let userId: string | undefined

    if (incomingKey && serverKey && incomingKey === serverKey) {
      userId = body.userId || process.env.SERVICE_USER_ID
      if (!userId) return jsonError('userId required for API key bypass', 400)
    } else {
      const session = await auth()
      if (!session?.user) return jsonError('Unauthorized', 401)
      userId = session.user.id
    }

    const response = await fetch(`${BACKEND_URL}/api/content`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': userId!
      },
      body: JSON.stringify({
        userId,
        title: body.title || 'Untitled',
        content: body.content || '',
        contentHtml: body.contentHtml || '',
        status: body.status || 'draft',
        type: body.type || 'article',
        metadata: body.metadata || {}
      })
    })

    if (!response.ok) {
      return jsonError('Failed to create content', response.status)
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    console.error('❌ [CONTENT-API][POST] Error:', error)
    return jsonError('Failed to create content', 500)
  }
}

export async function HEAD() {
  return new NextResponse(null, { status: 200 })
}