import { PrismaClient } from "@prisma/client";

declare global {
  // Prevent multiple instances in development
  // eslint-disable-next-line no-var
  var __prisma: PrismaClient | undefined;
}

export {};
export const prisma =
  global.__prisma ||
  new PrismaClient({
    log: ["query", "info", "warn", "error"],
  });
if (process.env.NODE_ENV !== "production") global.__prisma = prisma;
