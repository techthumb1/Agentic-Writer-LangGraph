# frontend/Dockerfile
FROM node:22-alpine AS base

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

# Alpine uses apk, not apt-get
RUN apk add --no-cache ca-certificates openssl

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --include=dev

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY prisma ./prisma
COPY . .

# Use build arg for Prisma generation (placeholder only)
ARG DATABASE_URL=postgresql://user:password@db:5432/ai_content_db

RUN npx prisma generate --schema=./prisma/schema.prisma

# Enable standalone output for production
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone build
#COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
#COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
#COPY --from=builder --chown=nextjs:nodejs /app/public ./public
#COPY --from=builder --chown=nextjs:nodejs /app/prisma ./prisma
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

USER nextjs
EXPOSE 3000

CMD ["node", ".next/server/app.js"]
