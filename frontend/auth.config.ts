//// frontend/auth.config.ts (Fixed version)
//
//import { NextAuthConfig } from 'next-auth';
//import Google from 'next-auth/providers/google';
//import Credentials from 'next-auth/providers/credentials';
//
//// Extend the Session type to include accessToken and picture
//declare module 'next-auth' {
//  interface Session {
//    accessToken?: string;
//    user: {
//      image?: string;
//      [key: string]: unknown;
//    };
//  }
//}
//
//export const authConfig = {
//  pages: {
//    signIn: '/auth/signin',
//    error: '/auth/error',
//  },
//  callbacks: {
//    authorized({ auth, request: { nextUrl } }) {
//      const isLoggedIn = !!auth?.user;
//      const isOnDashboard = nextUrl.pathname.startsWith('/dashboard');
//      const isOnGenerate = nextUrl.pathname.startsWith('/generate');
//      const isOnTemplates = nextUrl.pathname.startsWith('/templates');
//      const isOnSettings = nextUrl.pathname.startsWith('/settings');
//      const isOnContent = nextUrl.pathname.startsWith('/content');
//
//      // Protected routes - require authentication
//      if (isOnDashboard || isOnGenerate || isOnTemplates || isOnSettings || isOnContent) {
//        return isLoggedIn; // Return boolean, not Response.redirect
//      }
//      
//      // Allow access to all other routes (including home page)
//      return true;
//    },
//    jwt({ token, account, profile }) {
//      if (account && profile) {
//        token.accessToken = account.access_token;
//        token.picture = profile.picture;
//      }
//      return token;
//    },
//    session({ session, token }) {
//      if (token.accessToken) {
//        session.accessToken = token.accessToken as string;
//      }
//      if (token.picture) {
//        session.user.image = token.picture as string;
//      }
//      return session;
//    },
//  },
//  providers: [
//    Google({
//      clientId: process.env.AUTH_GOOGLE_ID!,
//      clientSecret: process.env.AUTH_GOOGLE_SECRET!,
//      authorization: {
//        params: {
//          prompt: "consent",
//          access_type: "offline",
//          response_type: "code"
//        }
//      }
//    }),
//    // Add credentials for testing
//    Credentials({
//      name: 'credentials',
//      credentials: {
//        email: { label: 'Email', type: 'email' },
//        password: { label: 'Password', type: 'password' },
//      },
//      async authorize(credentials) {
//        // Simple test authentication
//        if (
//          credentials?.email === 'test@example.com' &&
//          credentials?.password === 'password'
//        ) {
//          return {
//            id: '1',
//            name: 'Test User',
//            email: 'test@example.com',
//            image: null,
//          };
//        }
//        return null;
//      },
//    }),
//  ],
//  secret: process.env.AUTH_SECRET,
//  trustHost: true,
//} satisfies NextAuthConfig;

// File: frontend/auth.config.ts
// NextAuth.js v5 configuration

// File: frontend/auth.config.ts
import type { NextAuthConfig } from 'next-auth';

declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      email: string;
      name?: string | null;
      image?: string | null;
    };
  }
  
  interface JWT {
    id: string;
  }
}

export const authConfig = {
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
    verifyRequest: '/auth/verify-request',
    newUser: '/dashboard',
  },
  
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isOnDashboard = nextUrl.pathname.startsWith('/dashboard');
      const isOnGenerate = nextUrl.pathname.startsWith('/generate');
      const isOnTemplates = nextUrl.pathname.startsWith('/templates');
      const isOnSettings = nextUrl.pathname.startsWith('/settings');
      const isOnContent = nextUrl.pathname.startsWith('/content');
      const isOnProfile = nextUrl.pathname.startsWith('/profile');

      const isProtectedRoute = isOnDashboard || isOnGenerate || isOnTemplates || isOnSettings || isOnContent || isOnProfile;

      if (isProtectedRoute && !isLoggedIn) {
        return false;
      }

      return true;
    },

    async jwt({ token, user, account, trigger, session }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
        token.name = user.name;
        token.picture = user.image;
      }

      if (account) {
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
      }

      if (trigger === 'update' && session) {
        token.name = session.name;
        token.picture = session.image;
      }

      return token;
    },

    async session({ session, token, user }) {
      if (token && session.user) {
        session.user.id = token.id as string;
        session.user.email = token.email as string;
        session.user.name = token.name as string | null;
        session.user.image = token.picture as string | null;
      }

      if (user && session.user) {
        session.user.id = user.id;
      }

      return session;
    },

    async signIn({ user, account, credentials, email }) {
      if (account?.provider === 'google') {
        return true;
      }

      if (credentials) {
        return true;
      }

      if (email && user?.email) {
        return true;
      }

      return false;
    },
  },

  session: {
    strategy: 'database',
    maxAge: 30 * 24 * 60 * 60,
    updateAge: 24 * 60 * 60,
  },

  cookies: {
    sessionToken: {
      name: process.env.NODE_ENV === 'production' 
        ? '__Secure-next-auth.session-token'
        : 'next-auth.session-token',
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      },
    },
  },

  debug: process.env.NODE_ENV === 'development',
  trustHost: true,
  secret: process.env.AUTH_SECRET,
  providers: [], // Providers are defined in auth.ts
} satisfies NextAuthConfig;