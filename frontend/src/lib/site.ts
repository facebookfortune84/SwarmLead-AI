/**
 * Site-wide domain configuration — single source of truth for the frontend.
 *
 * Mirrors `core/site.py` on the backend. Everything derives from ONE value:
 *   NEXT_PUBLIC_SITE_URL="https://my-brand.com"   (or SITE_URL at build time)
 *
 * A domain switch is a one-line env change + rebuild. Optional overrides:
 *   NEXT_PUBLIC_API_URL / API_BACKEND_URL  — backend origin (defaults to api.*)
 */

function env(name: string): string | undefined {
  return process.env[name];
}

function stripScheme(value: string): string {
  return value
    .trim()
    .replace(/^https?:\/\//, "")
    .replace(/\/+$/, "");
}

export const PUBLIC_DOMAIN: string = stripScheme(
  env("NEXT_PUBLIC_DOMAIN") ||
    env("SITE_URL") ||
    env("NEXT_PUBLIC_SITE_URL") ||
    "realms2riches.com"
);

export const SITE_URL: string = (
  env("SITE_URL") ||
  env("NEXT_PUBLIC_SITE_URL") ||
  `https://${PUBLIC_DOMAIN}`
).replace(/\/+$/, "");

export const API_URL: string = (
  env("NEXT_PUBLIC_API_URL") ||
  env("API_BACKEND_URL") ||
  `https://api.${PUBLIC_DOMAIN}`
).replace(/\/+$/, "");

/**
 * Origin for client-side rendering: always the browser's current origin.
 *
 * In dynamic tunnel mode the public URL rotates daily; the browser is
 * sitting on the current tunnel URL, so `window.location.origin` is the
 * one value that can never go stale. Falls back to the baked SITE_URL when
 * rendered server-side (use `requestOrigin()` from lib/server-site there).
 */
export function currentOrigin(): string {
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  return SITE_URL;
}

export const APP_NAME: string = env("NEXT_PUBLIC_APP_NAME") || "Genesis Forge";

export function shareLink(network: string, url: string, text: string): string {
  const u = encodeURIComponent(url);
  const t = encodeURIComponent(text);
  switch (network) {
    case "x":
      return `https://twitter.com/intent/tweet?text=${t}&url=${u}`;
    case "facebook":
      return `https://www.facebook.com/sharer/sharer.php?u=${u}`;
    case "linkedin":
      return `https://www.linkedin.com/sharing/share-offsite/?url=${u}`;
    case "whatsapp":
      return `https://wa.me/?text=${t}%20${u}`;
    case "email":
      return `mailto:?subject=${encodeURIComponent("Genesis Forge")}&body=${t}%20${u}`;
    default:
      return url;
  }
}