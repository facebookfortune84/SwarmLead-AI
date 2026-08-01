import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Profile",
  description:
    "Manage your Genesis account profile, personal information, and preferences.",
  alternates: { canonical: "/profile" },
  robots: { index: false, follow: false },
};

export default function profileLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

