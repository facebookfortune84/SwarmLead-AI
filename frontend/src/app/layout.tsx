import type { Metadata } from "next";
import "./globals.css";

import { AppThemeProvider } from "@/components/providers/theme-provider";
import { QueryProvider } from "@/components/providers/query-provider";
import { Toaster } from "@/components/ui/sonner";
import { APP_NAME, PUBLIC_DOMAIN, SITE_URL } from "@/lib/site";

const siteUrl = SITE_URL;

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Genesis Forge — Autonomous Business Launch Platform by Realms 2 Riches",
    template: "%s | Genesis Forge",
  },
  description:
    "Genesis Forge by Realms 2 Riches is the first autonomous business launch platform powered by constitutional voice AI. Launch your business with your voice.",
  applicationName: "Genesis Forge",
  keywords: [
    "AI business launch",
    "voice AI",
    "autonomous business platform",
    "lead generation",
    "workflow automation",
    "constitutional AI",
    "AI agents",
    "launch your business with your voice",
  ],
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "Genesis Forge — Autonomous Business Launch Platform",
    description:
      "Launch your business with your voice. Genesis Forge by Realms 2 Riches — the first autonomous business platform powered by constitutional voice AI.",
    url: siteUrl,
    siteName: "Genesis Forge",
    type: "website",
    locale: "en_US",
    images: [
      {
        url: `${siteUrl}/genesis_forge_hero_image_1.png`,
        width: 1200,
        height: 630,
        alt: "Genesis — Autonomous Business Launch Platform",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Genesis Forge — Autonomous Business Launch Platform",
    description:
      "Launch your business with your voice. Genesis Forge by Realms 2 Riches — the first autonomous business platform powered by constitutional voice AI.",
    images: [`${siteUrl}/genesis_forge_hero_image_1.png`],
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: "/voice_agent_image_1.png",
    apple: "/voice_agent_image_1.png",
  },
  manifest: "/manifest.webmanifest",
  other: {
    "theme-color": "#0a0a1a",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <AppThemeProvider>
          <QueryProvider>
            {children}
            <Toaster position="bottom-right" richColors />
          </QueryProvider>
        </AppThemeProvider>
      </body>
    </html>
  );
}
