import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Live AI Business Launch Demo",
  description:
    "See Genesis in action — an interactive demonstration of how constitutional voice AI launches and runs your business, from lead qualification to workflow automation.",
  alternates: { canonical: "/demo" },
};

export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
