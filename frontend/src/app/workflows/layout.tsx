import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Workflows",
  description:
    "Automate outreach, SEO, traffic generation, and follow-up with prebuilt Genesis workflow templates and custom workflows.",
  alternates: { canonical: "/workflows" },
  robots: { index: false, follow: false },
};

export default function workflowsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

