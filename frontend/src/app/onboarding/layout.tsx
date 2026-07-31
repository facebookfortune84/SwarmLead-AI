import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Get Started — Launch Your Business",
  description:
    "Create your Genesis account and launch your business with your voice. No credit card required.",
  alternates: { canonical: "/onboarding" },
};

export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
