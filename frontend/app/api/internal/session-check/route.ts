// frontend/app/api/internal/session-check/route.ts
import { auth } from '@/app/api/auth/[...nextauth]/route'
import { NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function GET() {
  const session = await auth()
  return NextResponse.json({ 
    authenticated: !!session?.user,
    user: session?.user || null 
  })
}