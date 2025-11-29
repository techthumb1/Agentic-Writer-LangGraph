// frontend/lib/prisma.node.ts
import { PrismaClient } from '@prisma/client'

const dbUrl = process.env.DATABASE_URL || '';
const isCI = process.env.CI === 'true';
const isProd = process.env.NODE_ENV === 'production';

// -------------------------------
// Enterprise fail-fast validation
// -------------------------------

// 1. Validate DB name only in real prod (never in CI, never in local dev)
if (isProd && !isCI && !dbUrl.includes('ai_content_db')) {
  throw new Error(
    `[prisma.node] FATAL: DATABASE_URL must target ai_content_db. Current: ${dbUrl}`
  );
}

// 2. Validate Docker hostname only in real prod (skip in CI, skip in dev)
if (isProd && !isCI && !dbUrl.includes('@db:5432')) {
  throw new Error(
    `[prisma.node] FATAL: Production must use Docker hostname 'db:5432'. Current: ${dbUrl}`
  );
}

// Safe log in local dev
if (!isProd && !isCI) {
  console.log('[prisma.node] ✓ Using DB:', dbUrl.split('@')[1]?.split('/')[0] || 'unknown');
}

declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined
}

export const prisma =
  global.prisma ??
  new PrismaClient({
    log: ['error', 'warn'],
  });

if (!isProd) global.prisma = prisma;
