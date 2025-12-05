// File: frontend/app/api/content/[contentID]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'

export const runtime = 'nodejs'

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ contentID: string }> }
) {
  const params = await context.params
  const session = await auth()
  
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const response = await fetch(`${BACKEND_URL}/api/content/${params.contentID}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': session.user.id!
      },
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      return NextResponse.json({ error: 'Content not found' }, { status: 404 })
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    console.error('Content fetch error:', error)
    return NextResponse.json({ error: 'Failed to fetch content' }, { status: 500 })
  }
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ contentID: string }> }
) {
  const params = await context.params
  const session = await auth()
  const body = await request.json()
  
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const response = await fetch(`${BACKEND_URL}/api/content/${params.contentID}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': session.user.id!
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      return NextResponse.json({ error: 'Update failed' }, { status: response.status })
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    console.error('Content update error:', error)
    return NextResponse.json({ error: 'Failed to update content' }, { status: 500 })
  }
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ contentID: string }> }
) {
  const params = await context.params
  const session = await auth()
  
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const response = await fetch(`${BACKEND_URL}/api/content/${params.contentID}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': session.user.id!
      },
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      return NextResponse.json({ error: 'Delete failed' }, { status: response.status })
    }

    return NextResponse.json({ success: true, message: 'Content deleted successfully' })
  } catch (error) {
    console.error('Content delete error:', error)
    return NextResponse.json({ error: 'Failed to delete content' }, { status: 500 })
  }
}