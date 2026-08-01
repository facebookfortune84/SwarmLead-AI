import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Cancel Subscription",
  description:
    "Cancel your Genesis subscription. Manage your plan and account status.",
  alternates: { canonical: "/cancel" },
  robots: { index: false, follow: false },
};

export default function cancelLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

