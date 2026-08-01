import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Settings",
  description:
    "Configure your Genesis workspace - general settings, notifications, security, integrations, and voice agent preferences.",
  alternates: { canonical: "/settings" },
  robots: { index: false, follow: false },
};

export default function settingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

