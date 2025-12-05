// frontend/app/api/user/profile/avatar/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'

export const runtime = 'nodejs'

export async function POST(request: NextRequest) {
  const session = await auth()
  
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const formData = await request.formData()
    const file = formData.get('avatar') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      return NextResponse.json({ error: 'File must be an image' }, { status: 400 })
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      return NextResponse.json({ error: 'File too large (max 5MB)' }, { status: 400 })
    }

    // Forward to backend API
    const backendFormData = new FormData()
    backendFormData.append('avatar', file)
    backendFormData.append('userId', session.user.id!)

    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL
    const response = await fetch(`${backendUrl}/api/user/avatar`, {
      method: 'POST',
      body: backendFormData,
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      }
    })

    if (!response.ok) {
      throw new Error('Backend upload failed')
    }

    const data = await response.json()
    
    return NextResponse.json({ 
      success: true, 
      avatarUrl: data.avatarUrl 
    })

  } catch (error) {
    console.error('Avatar upload error:', error)
    return NextResponse.json(
      { error: 'Failed to upload avatar' }, 
      { status: 500 }
    )
  }
}