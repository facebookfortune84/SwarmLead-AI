import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Notifications",
  description:
    "Platform alerts, workflow status, outreach activity, and tenant events in one notification center.",
  alternates: { canonical: "/notifications" },
  robots: { index: false, follow: false },
};

export default function notificationsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

