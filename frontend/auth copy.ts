//import NextAuth from 'next-auth';
//import { authConfig } from './auth.config';
//import CredentialsProvider from 'next-auth/providers/credentials';
//import GoogleProvider from 'next-auth/providers/google';
//import { compare } from 'bcryptjs';
//import { prisma } from '@/lib/prisma.node.node';
//
//export const { auth, handlers, signIn, signOut } = NextAuth({
//  ...authConfig,
//  providers: [
//    GoogleProvider({
//      clientId: process.env.GOOGLE_CLIENT_ID!,
//      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
//    }),
//    CredentialsProvider({
//      name: 'credentials',
//      credentials: {
//        email: { label: "Email", type: "email" },
//        password: { label: "Password", type: "password" }
//      },
//      async authorize(credentials) {
//        if (!credentials?.email || !credentials?.password) {
//          throw new Error('Email and password required');
//        }
//
//        const user = await prisma.user.findUnique({
//          where: { email: credentials.email as string }
//        });
//
//        if (!user || !user.password) {
//          throw new Error('Invalid email or password');
//        }
//
//        if (!user.emailVerified) {
//          throw new Error('Please verify your email before signing in');
//        }
//
//        const isValid = await compare(credentials.password as string, user.password);
//
//        if (!isValid) {
//          throw new Error('Invalid email or password');
//        }
//
//        return {
//          id: user.id,
//          email: user.email,
//          name: user.name,
//        };
//      }
//    })
//  ],
//  session: {
//    strategy: 'jwt',
//    maxAge: 30 * 24 * 60 * 60,
//  },
//});

// File: frontend/lib/auth.ts
// NextAuth.js v5 with Prisma adapter for enterprise authentication

/// File: frontend/auth.ts
import NextAuth from 'next-auth';
import { PrismaAdapter } from '@auth/prisma-adapter';
import GoogleProvider from 'next-auth/providers/google';
import CredentialsProvider from 'next-auth/providers/credentials';
import { compare } from 'bcryptjs';
import { authConfig } from '@/auth.config';
import { prisma } from '@/lib/prisma.node';

export const { auth, handlers, signIn, signOut } = NextAuth({
  ...authConfig,
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.AUTH_GOOGLE_ID!,
      clientSecret: process.env.AUTH_GOOGLE_SECRET!,
      authorization: {
        params: {
          prompt: 'consent',
          access_type: 'offline',
          response_type: 'code',
        },
      },
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.name,
          email: profile.email,
          image: profile.picture,
          emailVerified: profile.email_verified ? new Date() : null,
        };
      },
    }),
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email', placeholder: 'you@example.com' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error('Email and password required');
        }

        try {
          const user = await prisma.user.findUnique({
            where: { email: credentials.email as string },
          });

          if (!user || !user.password) {
            throw new Error('Invalid email or password');
          }

          if (!user.emailVerified) {
            throw new Error('Please verify your email before signing in');
          }

          const isValid = await compare(credentials.password as string, user.password);
          if (!isValid) {
            throw new Error('Invalid email or password');
          }

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            image: user.image,
            emailVerified: user.emailVerified,
          };
        } catch (error) {
          if (process.env.NODE_ENV === 'development') {
            console.error('Auth error:', error);
          }
          throw error;
        }
      },
    }),
  ],
  events: {
    async signIn({ user, account, isNewUser }) {
      if (process.env.NODE_ENV === 'development') {
        console.log('User signed in:', { userId: user.id, provider: account?.provider, isNewUser });
      }
    },
    async signOut() {
      if (process.env.NODE_ENV === 'development') {
        console.log('User signed out');
      }
    },
  },
});