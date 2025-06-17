// File: frontend/auth.ts
// Create this new file in the frontend root directory

import NextAuth from 'next-auth';
import { authConfig } from './auth.config';

export const { auth, handlers, signIn, signOut } = NextAuth({
  ...authConfig,
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
});