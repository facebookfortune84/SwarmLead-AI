import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pricing & Billing",
  description:
    "Genesis plans and billing - manage your subscription, invoices, and payment methods for the autonomous business launch platform.",
  alternates: { canonical: "/billing" },
  robots: { index: false, follow: false },
};

export default function billingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

