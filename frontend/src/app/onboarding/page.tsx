"use client";

import { useRouter } from "next/navigation";
import { OnboardingWizard } from "@/components/onboarding/OnboardingWizard";

export default function OnboardingPage() {
  const router = useRouter();

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-primary-50/30 to-white">
      <OnboardingWizard
        onComplete={(data) => {
          console.log("onboarding complete", data);
          router.push("/dashboard");
        }}
        onSkip={() => router.push("/dashboard")}
      />
    </main>
  );
}
