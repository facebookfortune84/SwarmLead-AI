FROM node:20.20.2-alpine3.23 AS builder

ARG API_BACKEND_URL=http://api:8000
ENV API_BACKEND_URL=$API_BACKEND_URL
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci && npm cache clean --force

COPY . .
ENV NODE_ENV=production
RUN npm run build

FROM node:20.20.2-alpine3.23 AS runner

ARG API_BACKEND_URL=http://api:8000
ENV API_BACKEND_URL=$API_BACKEND_URL
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME=0.0.0.0

WORKDIR /app

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

USER nextjs

EXPOSE 3000

CMD ["node_modules/.bin/next", "start"]