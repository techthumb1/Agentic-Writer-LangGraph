import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get('token');

  if (!token) {
    return NextResponse.redirect(new URL('/auth/signin?error=invalid_token', req.url));
  }

  try {
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${backendUrl}/api/auth/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      },
      body: JSON.stringify({ token })
    });

    if (!response.ok) {
      return NextResponse.redirect(new URL('/auth/signin?error=token_expired', req.url));
    }

    return NextResponse.redirect(new URL('/auth/signin?verified=true', req.url));
  } catch (error) {
    console.error('Verification error:', error);
    return NextResponse.redirect(new URL('/auth/signin?error=verification_failed', req.url));
  }
}