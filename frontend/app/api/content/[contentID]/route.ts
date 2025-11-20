// File: frontend/app/api/content/[contentID]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma.node'

export const runtime = 'nodejs'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ contentID: string }> }
) {
  const params = await context.params
  const session = await auth()
  
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Try Prisma first
  try {
    const content = await prisma.content.findFirst({
      where: {
        id: params.contentID,
        userId: session.user.id,
      }
    })

    if (content) {
      const wordCount = content.content.split(/\s+/).filter((w: string) => w.length > 0).length
      const readingTime = Math.ceil(wordCount / 200)

      return NextResponse.json({
        id: content.id,
        title: content.title,
        content: content.content,
        contentHtml: content.contentHtml,
        status: content.status,
        type: content.type,
        createdAt: content.createdAt.toISOString(),
        updatedAt: content.updatedAt.toISOString(),
        views: content.views,
        author: session.user.name,
        metadata: {
          wordCount,
          readingTime,
          ...((content.metadata as Record<string, unknown>) || {})
        }
      })
    }
  } catch (error) {
    console.error('Prisma lookup failed:', error)
  }

  // Fall back to backend API for generated content
  const response = await fetch(`${BACKEND_URL}/api/content/${params.contentID}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    return NextResponse.json({ error: 'Content not found' }, { status: 404 })
  }

  return NextResponse.json(await response.json())
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

  // Try Prisma update
  try {
    const updated = await prisma.content.update({
      where: {
        id: params.contentID,
        userId: session.user.id,
      },
      data: {
        title: body.title,
        content: body.content,
        contentHtml: body.contentHtml,
        status: body.status,
        metadata: body.metadata,
      }
    })

    return NextResponse.json({
      success: true,
      contentId: updated.id,
      updatedAt: updated.updatedAt.toISOString()
    })
  } catch (error) {
    console.error('Prisma update failed, trying backend:', error)
  }

  // Fall back to backend
  const response = await fetch(`${BACKEND_URL}/api/content/${params.contentID}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`Backend API error: ${response.status}`)
  }

  return NextResponse.json(await response.json())
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

  // Try Prisma delete
  try {
    await prisma.content.delete({
      where: {
        id: params.contentID,
        userId: session.user.id,
      }
    })

    return NextResponse.json({
      success: true,
      message: 'Content deleted successfully'
    })
  } catch (error) {
    console.error('Prisma delete failed, trying backend:', error)
  }

  // Fall back to backend
  const response = await fetch(`${BACKEND_URL}/api/content/${params.contentID}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`Backend API error: ${response.status}`)
  }

  return NextResponse.json(await response.json())
}