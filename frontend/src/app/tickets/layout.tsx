import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Support Tickets",
  description:
    "Customer support, escalations, AI handoffs, and voice transfer in the Genesis ticket center.",
  alternates: { canonical: "/tickets" },
  robots: { index: false, follow: false },
};

export default function ticketsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

