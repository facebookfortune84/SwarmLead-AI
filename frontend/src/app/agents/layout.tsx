import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Agents",
  description:
    "Configure and monitor your Genesis AI agents - voice, onboarding, outreach, and workflow automation agents with real-time status and controls.",
  alternates: { canonical: "/agents" },
  robots: { index: false, follow: false },
};

export default function agentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

