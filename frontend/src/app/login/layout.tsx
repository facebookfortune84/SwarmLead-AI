import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sign In to Genesis",
  description:
    "Sign in to your Genesis account to manage leads, workflows, outreach campaigns, and AI voice agents.",
  alternates: { canonical: "/login" },
  robots: { index: false, follow: false },
};

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
