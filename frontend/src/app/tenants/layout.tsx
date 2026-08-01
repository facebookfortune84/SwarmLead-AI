import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tenant Management",
  description:
    "Manage your Genesis company tenants, infrastructure provisioning, and deployment status.",
  alternates: { canonical: "/tenants" },
  robots: { index: false, follow: false },
};

export default function tenantsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

