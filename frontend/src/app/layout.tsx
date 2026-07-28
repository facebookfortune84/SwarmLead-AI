import type { Metadata } from "next";
import "./globals.css";

import { AppThemeProvider } from "@/components/providers/theme-provider";
import { QueryProvider } from "@/components/providers/query-provider";

export const metadata: Metadata = {
  title: {
    default: "Genesis — Autonomous Business Launch Platform",
    template: "%s | Genesis",
  },
  description:
    "Genesis is the first autonomous business launch platform powered by constitutional voice AI. Launch your business with your voice.",
  openGraph: {
    title: "Genesis — Autonomous Business Launch Platform",
    description:
      "Launch your business with your voice. The first autonomous business platform powered by constitutional voice AI.",
    url: process.env.SITE_URL || "https://realms2riches.com",
    siteName: "Genesis",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "Genesis — Autonomous Business Launch Platform",
    description:
      "Launch your business with your voice. The first autonomous business platform powered by constitutional voice AI.",
  },
  robots: {
    index: true,
    follow: true,
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
          </QueryProvider>
        </AppThemeProvider>
      </body>
    </html>
  );
}
