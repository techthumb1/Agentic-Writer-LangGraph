# frontend/Dockerfile

# ---- base ----
FROM node:22-alpine AS base

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends ca-certificates openssl \
    && rm -rf /var/lib/apt/lists/*

# ---- deps ----
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --include=dev

# ---- builder ----
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules

# Copy prisma schema and migrations BEFORE other files
COPY prisma ./prisma

# Copy entire source
COPY . .

# Force correct DATABASE_URL for Prisma generation
ENV DATABASE_URL="postgresql://postgres:LwfO+JkzB4v7cqDHbGb+5QOgWxsyGlu6@db:5432/ai_content_db"

# Generate Prisma client before build
RUN npx prisma generate --schema=./prisma/schema.prisma

# Build Next.js app
RUN npm run build

# ---- runner ----
FROM base AS runner
WORKDIR /app
ENV PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NODE_ENV=production \
    DATABASE_URL="postgresql://postgres:LwfO+JkzB4v7cqDHbGb+5QOgWxsyGlu6@db:5432/ai_content_db"
RUN useradd -m -u 1001 nextjs

# Copy public assets
COPY --from=builder /app/public ./public

# Copy entire .next directory (includes all pages)
COPY --from=builder /app/.next ./.next

# Copy source app directory
COPY --from=builder /app/app ./app

# Copy node_modules
COPY --from=builder /app/node_modules ./node_modules

# Copy Prisma files
COPY --from=builder /app/prisma ./prisma

# Copy package.json
COPY --from=builder /app/package.json ./package.json

# Ensure nextjs user owns all files
RUN chown -R nextjs:nextjs /app

USER nextjs
EXPOSE 3000

CMD ["npm", "start"]