import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma.node'

export const runtime = 'nodejs' // Forces Node runtime

export async function GET() {
  const users = await prisma.user.findMany({
    select: { id: true, email: true },
    take: 1,
  })
  return NextResponse.json({ ok: true, count: users.length })
}
