// frontend/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// ==============================================
// Edge-safe Middleware — No Node/Prisma Imports
// Delegates user verification to Node API layer
// ==============================================

// Routes for redirect logic
const authRoutes = ['/auth/signin', '/auth/signup']
const protectedRoutes = ['/dashboard', '/generate', '/content', '/templates', '/settings']

export const config = {
  matcher: [
    '/((?!api/auth|api/internal|_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.jpg$|.*\\.jpeg$|.*\\.gif$|.*\\.svg$).*)',
  ],
}

export default async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip static and internal assets
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/api/') ||
    pathname.startsWith('/static/') ||
    pathname.includes('.') ||
    pathname.startsWith('/favicon')
  ) {
    return NextResponse.next()
  }

  // ===========================================================
  // Delegate session validation to secure Node-side endpoint
  // ===========================================================
  let isAuthenticated = false
  try {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || request.nextUrl.origin
    const verifyUrl = `${baseUrl}/api/internal/session-check`
    const res = await fetch(verifyUrl, {
      method: 'GET',
      headers: { cookie: request.headers.get('cookie') || '' },
      cache: 'no-store',
    })
    if (res.ok) {
      const data = await res.json()
      isAuthenticated = !!data?.authenticated
    }
  } catch {
    // Edge-safe: never throw here
    isAuthenticated = false
  }

  // Route categorization
  const isAuthRoute = authRoutes.includes(pathname)
  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route))

  // Redirect logic
  if (isAuthenticated && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  if (!isAuthenticated && isProtectedRoute) {
    const signinUrl = new URL('/auth/signin', request.url)
    signinUrl.searchParams.set('callbackUrl', pathname)
    return NextResponse.redirect(signinUrl)
  }

  // Allow normal flow
  return NextResponse.next()
}
