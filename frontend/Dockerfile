FROM node:20.20.2-alpine3.23 AS builder

ARG API_BACKEND_URL=http://api:8000
ARG NEXT_PUBLIC_DOMAIN=realms2riches.com
ENV API_BACKEND_URL=$API_BACKEND_URL
ENV NEXT_PUBLIC_DOMAIN=$NEXT_PUBLIC_DOMAIN
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci && npm cache clean --force

COPY . .
ENV NODE_ENV=production
RUN npm run build

FROM node:20.20.2-alpine3.23 AS runner

ARG API_BACKEND_URL=http://api:8000
ARG NEXT_PUBLIC_DOMAIN=localhost:3000
ENV API_BACKEND_URL=$API_BACKEND_URL
ENV NEXT_PUBLIC_DOMAIN=$NEXT_PUBLIC_DOMAIN
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME=0.0.0.0

WORKDIR /app

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
