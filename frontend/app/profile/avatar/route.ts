// frontend/app/api/user/profile/avatar/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma.node'
import { writeFile } from 'fs/promises'
import { join } from 'path'

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

    // Convert to buffer
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)

    // Generate unique filename
    const timestamp = Date.now()
    const extension = file.name.split('.').pop()
    const filename = `${session.user.id}_${timestamp}.${extension}`
    
    // Save to public/avatars directory
    const publicPath = join(process.cwd(), 'public', 'avatars')
    const filePath = join(publicPath, filename)
    
    await writeFile(filePath, buffer)

    // Update user in database
    const avatarUrl = `/avatars/${filename}`
    await prisma.user.update({
      where: { id: session.user.id },
      data: { image: avatarUrl }
    })

    return NextResponse.json({ 
      success: true, 
      avatarUrl 
    })

  } catch (error) {
    console.error('Avatar upload error:', error)
    return NextResponse.json(
      { error: 'Failed to upload avatar' }, 
      { status: 500 }
    )
  }
}