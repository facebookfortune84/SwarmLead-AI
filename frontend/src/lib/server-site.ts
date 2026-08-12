/**
 * Server-side origin resolution — the frontend half of the tunnel auto-pilot.
 *
 * The Quick Tunnel URL rotates daily, so SSR-rendered assets (sitemap,
 * robots.txt, metadataBase, OG URLs) must derive the public origin from the
 * incoming request rather than a build-time constant. Next.js Route
 * Handlers and Server Components read the `Host` header per request —
 * the host the browser actually used is, by definition, the current
 * public origin.
 *
 * Resolution order:
 *   1. `SITE_URL` env (explicit override, e.g. a permanent domain).
 *   2. `Host` header of the current request (dynamic tunnel URL).
 *   3. Baked `NEXT_PUBLIC_DOMAIN` fallback (last resort).
 */

import { headers } from "next/headers";

import { PUBLIC_DOMAIN, SITE_URL } from "./site";

const SCHEME_BY_HOST: Record<string, string> = {
  localhost: "http",
  "127.0.0.1": "http",
};

export async function requestOrigin(): Promise<string> {
  const explicit = process.env.SITE_URL || process.env.NEXT_PUBLIC_SITE_URL;
  if (explicit) return explicit.replace(/\/+$/, "");

  try {
    const headerList = await headers();
    const host = headerList.get("host");
    if (host) {
      const bareHost = host.trim();
      if (bareHost) {
        const scheme = SCHEME_BY_HOST[bareHost.split(":")[0]] || "https";
        return `${scheme}://${bareHost}`;
      }
    }
  } catch {
    // headers() is unavailable in static generation contexts — fall through.
  }

  return SITE_URL;
}

export { PUBLIC_DOMAIN };
