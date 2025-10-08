import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get('token');

  if (!token) {
    return NextResponse.redirect(new URL('/auth/signin?error=invalid_token', req.url));
  }

  const user = await prisma.user.findFirst({
    where: {
      verificationToken: token,
      tokenExpires: { gt: new Date() }
    }
  });

  if (!user) {
    return NextResponse.redirect(new URL('/auth/signin?error=token_expired', req.url));
  }

  await prisma.user.update({
    where: { id: user.id },
    data: {
      emailVerified: new Date(),
      verificationToken: null,
      tokenExpires: null
    }
  });

  return NextResponse.redirect(new URL('/auth/signin?verified=true', req.url));
}