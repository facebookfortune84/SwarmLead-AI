import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Lead Management",
  description:
    "Manage your inbound leads, qualification scores, and timeline activity in the Genesis lead intelligence dashboard.",
  alternates: { canonical: "/leads" },
  robots: { index: false, follow: false },
};

export default function leadsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

