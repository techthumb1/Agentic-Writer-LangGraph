import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";
import { prisma } from "@/lib/prisma.node";
import { compare } from "bcryptjs";

type UserWithPassword = {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  password?: string | null;
  passwordHash?: string | null;
  hashedPassword?: string | null;
};

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
        //secret: process.env.AUTH_SECRET,
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

        const dbUser = (await prisma.user.findUnique({
          where: { email },
        })) as UserWithPassword | null;

        if (!dbUser) {
          console.log('[AUTH] User not found');
          return null;
        }

        const storedHash = dbUser.passwordHash ?? dbUser.hashedPassword ?? dbUser.password ?? null;

        if (!storedHash) return null;

        const isValid = await compare(creds.password, storedHash);

        if (!isValid) return null;

        return { id: dbUser.id, email: dbUser.email, name: dbUser.name, image: dbUser.image };
      },
    }),
  ],

  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },

  // Replace callbacks section (lines 69-98):
  callbacks: {
  async jwt({ token, user, account }) {
    if (user) {
      // For credentials, user object already has DB id from authorize()
      // For OAuth, we need to look up the existing user
      if (account?.provider === 'google') {
        const existing = await prisma.user.findUnique({
          where: { email: user.email!.toLowerCase().trim() }
        });
        
        if (existing) {
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
        // Credentials - use the ID from authorize()
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
      const email = user.email.toLowerCase().trim();
      const existing = await prisma.user.findUnique({
        where: { email },
      });
      if (existing) {
        // User exists - ensure JWT gets the DB ID
        user.id = existing.id;
        await prisma.user.update({
          where: { email },
          data: {
            name: user.name ?? existing.name,
            image: user.image ?? existing.image,
          },
        });
        return;
      }
      // New user - create with the ID from authorize/Google
      await prisma.user.create({
        data: {
          id: user.id, // Use the ID from the provider
          email,
          name: user.name ?? null,
          image: user.image ?? null,
        },
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
