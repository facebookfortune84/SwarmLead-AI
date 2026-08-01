import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Outreach Campaigns",
  description:
    "Launch email and voice outreach campaigns powered by Genesis AI agents. Templates, sequences, and follow-up automation.",
  alternates: { canonical: "/outreach" },
  robots: { index: false, follow: false },
};

export default function outreachLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

