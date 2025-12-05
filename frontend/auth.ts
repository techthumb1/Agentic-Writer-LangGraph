import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;

export const { handlers, auth, signIn, signOut } = NextAuth({
  session: {
    strategy: "jwt",
  },

  cookies: {
    sessionToken: {
      name: "next-auth.session-token",
      options: {
        httpOnly: true,
        sameSite: "lax",
        secure: false,
        path: "/",
      },
    },
  },

  providers: [
    Google({
      clientId: process.env.AUTH_GOOGLE_ID!,
      clientSecret: process.env.AUTH_GOOGLE_SECRET!,
    }),

    Credentials({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },

      async authorize(rawCreds) {
        const creds = rawCreds as { email: string; password: string };
        if (!creds?.email || !creds?.password) {
          console.log('[AUTH] Missing credentials');
          return null;
        }

        const email = creds.email.trim().toLowerCase();

        const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
          },
          body: JSON.stringify({ email, password: creds.password })
        });

        if (!response.ok) {
          console.log('[AUTH] Login failed');
          return null;
        }

        const user = await response.json();
        return { id: user.id, email: user.email, name: user.name, image: user.image };
      },
    }),
  ],

  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },

  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        if (account?.provider === 'google') {
          const response = await fetch(`${BACKEND_URL}/api/auth/user-by-email`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
            },
            body: JSON.stringify({ email: user.email!.toLowerCase().trim() })
          });
          
          if (response.ok) {
            const existing = await response.json();
            token.id = existing.id;
            token.email = existing.email;
            token.name = user.name ?? existing.name;
            token.image = user.image ?? existing.image;
          } else {
            token.id = user.id;
            token.email = user.email;
            token.name = user.name;
            token.image = user.image ?? null;
          }
        } else {
          token.id = user.id;
          token.email = user.email;
          token.name = user.name;
          token.image = user.image ?? null;
        }
        
        if (account) token.provider = account.provider;
      }
      return token;
    },
    
    async session({ session, token }) {
      if (!session.user) {
        session.user = {
          id: "",
          email: "",
          name: "",
          image: null,
          emailVerified: null,
        } as typeof session.user;
      }
      session.user.id = token.id as string;
      session.user.email = token.email as string;
      session.user.name = token.name as string;
      session.user.image = (token.image as string) ?? null;
      return session;
    },
  },

  events: {
    async signIn({ user }) {
      try {
        if (!user?.email) return;
        
        await fetch(`${BACKEND_URL}/api/auth/sync-user`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
          },
          body: JSON.stringify({
            id: user.id,
            email: user.email.toLowerCase().trim(),
            name: user.name,
            image: user.image
          })
        });
      } catch (err) {
        console.error("[auth] Failed to sync user:", err);
      }
    },
  },

  secret: process.env.AUTH_SECRET,
  trustHost: true,
  debug: false,
});