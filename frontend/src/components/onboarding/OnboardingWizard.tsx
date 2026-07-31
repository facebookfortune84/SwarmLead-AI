"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, Sparkles, Building2, Users, Target, Mic, Rocket, Check } from "lucide-react";

interface OnboardingWizardProps {
  onComplete: (data: Record<string, string>) => void;
  onSkip?: () => void;
  initialStep?: number;
}

interface StepField {
  key: string;
  label: string;
  required: boolean;
  type?: string;
  placeholder?: string;
}

const STEPS: {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  fields: StepField[];
}[] = [
  {
    id: "business",
    title: "Tell Us About Your Business",
    description: "Help us understand what you do so we can tailor Genesis to your needs.",
    icon: Building2,
    fields: [
      { key: "full_name", label: "Your Full Name", required: true },
      { key: "business_name", label: "Business Name", required: true },
      { key: "email", label: "Email Address", required: true, type: "email" },
      { key: "password", label: "Create Password", required: true, type: "password" },
      { key: "industry", label: "Industry / Niche", required: false },
      { key: "website", label: "Website URL", required: false },
    ],
  },
  {
    id: "audience",
    title: "Define Your Target Audience",
    description: "Who are you trying to reach? We'll optimize lead generation for your ideal customer.",
    icon: Users,
    fields: [
      { key: "target_audience", label: "Describe Your Target Audience", required: false },
      { key: "audience_role", label: "Ideal Customer Role / Title", required: false },
      { key: "company_size", label: "Target Company Size", required: false },
    ],
  },
  {
    id: "goals",
    title: "Set Your Goals",
    description: "What do you want to achieve? This helps our AI prioritize your growth strategy.",
    icon: Target,
    fields: [
      { key: "primary_goal", label: "Primary Business Goal", required: false, placeholder: "Lead generation, brand awareness, sales..." },
      { key: "monthly_target", label: "Monthly Lead Target", required: false, type: "number" },
      { key: "timeline", label: "Desired Timeline", required: false, placeholder: "Immediately, 30 days, 90 days..." },
    ],
  },
  {
    id: "voice",
    title: "Configure Voice Agent",
    description: "Set up your AI voice agent's personality and communication style.",
    icon: Mic,
    fields: [
      { key: "voice_style", label: "Voice Style", required: false, placeholder: "Professional, friendly, casual..." },
      { key: "greeting_preference", label: "Greeting Preference", required: false, placeholder: "Formal introduction, casual hello..." },
      { key: "timezone", label: "Business Timezone", required: false },
      { key: "first_campaign", label: "First Campaign Name", required: false },
    ],
  },
  {
    id: "launch",
    title: "Ready to Launch",
    description: "You're all set! We'll create your account and set up your business.",
    icon: Rocket,
    fields: [],
  },
];

export function OnboardingWizard({ onComplete, onSkip, initialStep = 0 }: OnboardingWizardProps) {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(initialStep);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const currentStepData = STEPS[currentStep];
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === STEPS.length - 1;
  const progress = ((currentStep + 1) / STEPS.length) * 100;

  const handleNext = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError("");

    if (isLastStep) {
      setSubmitting(true);
      try {
        const registerPayload = {
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
        };

        const response = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(registerPayload),
        });
        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || "Registration failed.");
        }
        const data = await response.json();

        if (data.access_token) {
          localStorage.setItem("swarmlead_access_token", data.access_token);
        }
        if (data.refresh_token) {
          localStorage.setItem("swarmlead_refresh_token", data.refresh_token);
        }

        if (formData.business_name) {
          const slug = formData.business_name
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "");
          try {
            await fetch("/api/tenants/register", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${data.access_token}`,
              },
              body: JSON.stringify({
                name: formData.business_name,
                slug: slug || "my-company",
              }),
            });
          } catch {
            // tenant registration is secondary
          }
        }

        onComplete(formData);
        router.replace("/dashboard");
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Connection failed. Please check your network and try again.";
        setError(msg);
      } finally {
        setSubmitting(false);
      }
      return;
    }

    const requiredFields = currentStepData.fields.filter((f) => f.required);
    const missing = requiredFields.find((f) => !formData[f.key]);
    if (missing) {
      setError(`${missing.label} is required.`);
      return;
    }

    setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    setError("");
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const getAutocomplete = (key: string): string => {
    const map: Record<string, string> = {
      full_name: "name",
      email: "email",
      password: "new-password",
      business_name: "organization",
      phone: "tel",
      website: "url",
    };
    return map[key] || "off";
  };

  const getInputType = (key: string, fieldType?: string): string => {
    if (fieldType) return fieldType;
    if (key === "password") return "password";
    if (key === "email") return "email";
    return "text";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950/90 to-gray-950 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-violet-500/15 via-transparent to-transparent" />

      <div className="relative z-10 max-w-2xl mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-white font-semibold">Genesis Onboarding</span>
          </div>
          {onSkip && (
            <button
              type="button"
              onClick={onSkip}
              className="text-sm text-white/40 hover:text-white/60 transition-colors"
            >
              Skip for now
            </button>
          )}
        </motion.div>

        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-white/50">
              Step {currentStep + 1} of {STEPS.length}
            </span>
            <span className="text-sm text-white/50">{Math.round(progress)}%</span>
          </div>
          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
            />
          </div>
        </div>

        <div className="flex gap-2 mb-8">
          {STEPS.map((step, i) => (
            <div
              key={step.id}
              className={`flex-1 h-1 rounded-full transition-all duration-300 ${
                i <= currentStep ? "bg-indigo-500" : "bg-white/5"
              }`}
            />
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-8 shadow-2xl shadow-black/50">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
                  {(() => {
                    const Icon = currentStepData.icon;
                    return <Icon className="w-7 h-7 text-white" />;
                  })()}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">{currentStepData.title}</h2>
                  <p className="text-white/50">{currentStepData.description}</p>
                </div>
              </div>

              {isLastStep ? (
                <div className="text-center py-8">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-indigo-500/25">
                    <Check className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">You&apos;re All Set!</h3>
                  <p className="text-white/50 mb-6">
                    We&apos;ll create your account and set everything up. Click Launch to get started.
                  </p>
                  {formData.business_name && (
                    <div className="bg-white/5 rounded-xl p-4 mb-6 inline-block">
                      <p className="text-sm text-white/40">Setting up</p>
                      <p className="text-white font-medium">{formData.business_name}</p>
                    </div>
                  )}
                </div>
              ) : (
                <form onSubmit={handleNext} noValidate className="space-y-5">
                  {currentStepData.fields.map((field) => (
                    <div key={field.key}>
                      <label htmlFor={field.key} className="block text-sm font-medium mb-2 text-white/70">
                        {field.label}
                        {field.required && <span className="text-red-400 ml-1">*</span>}
                      </label>
                      <input
                        id={field.key}
                        type={getInputType(field.key, field.type)}
                        autoComplete={getAutocomplete(field.key)}
                        value={formData[field.key] || ""}
                        onChange={(e) =>
                          setFormData((prev) => ({ ...prev, [field.key]: e.target.value }))
                        }
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all"
                        placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                      />
                    </div>
                  ))}
                </form>
              )}

              {error && (
                <motion.p
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2"
                >
                  {error}
                </motion.p>
              )}

              <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/10">
                <button
                  onClick={handleBack}
                  disabled={isFirstStep || submitting}
                  className="px-6 py-3 text-white/50 hover:text-white/70 font-medium disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  Back
                </button>

                <div className="flex items-center gap-3">
                  <motion.button
                    onClick={handleNext}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={submitting}
                    className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? (
                      <span className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Creating Account...
                      </span>
                    ) : isLastStep ? (
                      <span>
                        Launch My Business
                        <ChevronRight className="w-4 h-4 ml-2 inline" />
                      </span>
                    ) : (
                      <span>
                        Continue
                        <ChevronRight className="w-4 h-4 ml-2 inline" />
                      </span>
                    )}
                  </motion.button>
                </div>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}