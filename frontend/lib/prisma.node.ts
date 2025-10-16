import { PrismaClient } from '@prisma/client'
// One-time debug
if (process.env.AUTH_DEBUG === "true") {
  try {
    const u = new URL(process.env.DATABASE_URL || "");
    console.log("[auth][debug] DB target:", { protocol: u.protocol, host: u.host, pathname: u.pathname });
  } catch {
    console.log("[auth][debug] DATABASE_URL not parseable");
  }
}

declare global {
  // Prevent hot-reload instantiations in dev
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined
}

export const prisma =
  global.prisma ??
  new PrismaClient({
    log: ['error', 'warn'],
  })

if (process.env.NODE_ENV !== 'production') global.prisma = prisma

// No process.on hooks — handled by container orchestration (Fastify/Next.js lifecycle)
