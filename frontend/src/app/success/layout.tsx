import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Checkout Complete",
  description:
    "Your Genesis checkout was successful. Continue setting up your business launch.",
  alternates: { canonical: "/success" },
  robots: { index: false, follow: false },
};

export default function successLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

