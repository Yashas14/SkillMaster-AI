FROM node:20-alpine
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate

WORKDIR /app

# Copy workspace config files
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml* ./

# Copy shared packages needed by bff
COPY packages/types ./packages/types

# Copy bff app
COPY apps/bff ./apps/bff

# Install bff dependencies (resolves workspace packages)
RUN pnpm install --filter @skillmaster/bff

WORKDIR /app/apps/bff

EXPOSE 4000

CMD ["npx", "tsx", "src/index.ts"]
