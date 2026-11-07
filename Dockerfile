FROM node:24-bookworm-slim AS builder

ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /workspace/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 make \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global pnpm@10.34.9

COPY app/package.json app/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

WORKDIR /workspace
COPY Makefile ./
COPY scripts/contracts.py scripts/contracts.py
COPY contracts contracts
COPY data/public data/public
COPY app app

ENV POLISCOPE_LIVE_EXTRACTION_ENABLED=false
RUN pnpm --dir app build

FROM node:24-bookworm-slim AS runner

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=3000 \
    POLISCOPE_LIVE_EXTRACTION_ENABLED=false

WORKDIR /app
COPY --from=builder --chown=node:node /workspace/app/.next/standalone ./
COPY --from=builder --chown=node:node /workspace/app/.next/static ./.next/static

USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:3000/').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"
CMD ["node", "server.js"]
