import type { Metadata } from "next";
import "./globals.css";

import { AppThemeProvider } from "@/components/providers/theme-provider";
import { QueryProvider } from "@/components/providers/query-provider";
import { Toaster } from "@/components/ui/sonner";

const siteUrl = process.env.SITE_URL || "https://realms2riches.com";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Genesis — Autonomous Business Launch Platform",
    template: "%s | Genesis",
  },
  description:
    "Genesis is the first autonomous business launch platform powered by constitutional voice AI. Launch your business with your voice.",
  applicationName: "Genesis",
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
    title: "Genesis — Autonomous Business Launch Platform",
    description:
      "Launch your business with your voice. The first autonomous business platform powered by constitutional voice AI.",
    url: siteUrl,
    siteName: "Genesis",
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
    title: "Genesis — Autonomous Business Launch Platform",
    description:
      "Launch your business with your voice. The first autonomous business platform powered by constitutional voice AI.",
    images: [`${siteUrl}/genesis_forge_hero_image_1.png`],
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: "/genesis_forge_logo_1.png",
    apple: "/genesis_forge_logo_1.png",
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
