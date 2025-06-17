// frontend/auth.config.ts (Fixed version)
import { NextAuthConfig } from 'next-auth';
import Google from 'next-auth/providers/google';
import Credentials from 'next-auth/providers/credentials';

// Extend the Session type to include accessToken and picture
declare module 'next-auth' {
  interface Session {
    accessToken?: string;
    user: {
      image?: string;
      [key: string]: unknown;
    };
  }
}

export const authConfig = {
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isOnDashboard = nextUrl.pathname.startsWith('/dashboard');
      const isOnGenerate = nextUrl.pathname.startsWith('/generate');
      const isOnTemplates = nextUrl.pathname.startsWith('/templates');
      const isOnSettings = nextUrl.pathname.startsWith('/settings');
      const isOnContent = nextUrl.pathname.startsWith('/content');

      // Protected routes - require authentication
      if (isOnDashboard || isOnGenerate || isOnTemplates || isOnSettings || isOnContent) {
        return isLoggedIn; // Return boolean, not Response.redirect
      }
      
      // Allow access to all other routes (including home page)
      return true;
    },
    jwt({ token, account, profile }) {
      if (account && profile) {
        token.accessToken = account.access_token;
        token.picture = profile.picture;
      }
      return token;
    },
    session({ session, token }) {
      if (token.accessToken) {
        session.accessToken = token.accessToken as string;
      }
      if (token.picture) {
        session.user.image = token.picture as string;
      }
      return session;
    },
  },
  providers: [
    Google({
      clientId: process.env.AUTH_GOOGLE_ID!,
      clientSecret: process.env.AUTH_GOOGLE_SECRET!,
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code"
        }
      }
    }),
    // Add credentials for testing
    Credentials({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        // Simple test authentication
        if (
          credentials?.email === 'test@example.com' &&
          credentials?.password === 'password'
        ) {
          return {
            id: '1',
            name: 'Test User',
            email: 'test@example.com',
            image: null,
          };
        }
        return null;
      },
    }),
  ],
  secret: process.env.AUTH_SECRET,
  trustHost: true,
} satisfies NextAuthConfig;