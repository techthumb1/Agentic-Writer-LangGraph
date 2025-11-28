// frontend/lib/prisma.node.ts

import { PrismaClient } from '@prisma/client'

const dbUrl = process.env.DATABASE_URL || '';

// Enterprise fail-fast: validate correct database
if (!dbUrl.includes('ai_content_db')) {
  throw new Error(
    `[prisma.node] FATAL: DATABASE_URL must target ai_content_db. Current: ${dbUrl}`
  );
}

// Validate Docker hostname in production
if (process.env.NODE_ENV === 'production' && !dbUrl.includes('@db:')) {
  throw new Error(
    `[prisma.node] FATAL: Production must use Docker hostname 'db'. Current: ${dbUrl}`
  );
}

console.log('[prisma.node] ✓ Connected to:', dbUrl.split('@')[1]?.split('/')[0]);

declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined
}

export const prisma =
  global.prisma ??
  new PrismaClient({
    log: ['error', 'warn'],
  })

if (process.env.NODE_ENV !== 'production') global.prisma = prisma