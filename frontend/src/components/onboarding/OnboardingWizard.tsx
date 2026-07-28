"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, Sparkles } from "lucide-react";
import { VoiceOrb } from "@/components/voice";

interface OnboardingWizardProps {
  onComplete: (data: Record<string, string>) => void;
  onSkip?: () => void;
  initialStep?: number;
}

const STEPS = [
  {
    id: "welcome",
    title: "Welcome to Genesis",
    description: "Your autonomous business operating system",
    voicePrompt: "Welcome to Genesis! I'm your AI assistant. Let's get you set up in minutes.",
    fields: [],
    optional: ["name", "company_name"],
    icon: "sparkles"
  },
  {
    id: "business_profile",
    title: "Business Profile",
    description: "Tell us about your business",
    voicePrompt: "Tell me about your business. What's your company name and what do you do?",
    fields: ["company_name", "industry", "description", "website"],
    optional: ["team_size", "stage", "funding"],
    icon: "briefcase"
  },
  {
    id: "goals",
    title: "Goals & Objectives",
    description: "Define what success looks like",
    voicePrompt: "What are your top 3 goals for the next 90 days?",
    fields: ["primary_goal", "target_metric", "timeline"],
    optional: ["secondary_goals", "budget"],
    icon: "target"
  },
  {
    id: "voice_setup",
    title: "Voice Assistant Setup",
    description: "Configure your voice assistant",
    voicePrompt: "Let's set up your voice assistant. Choose a voice and test it.",
    fields: ["voice_id", "language", "greeting_style"],
    optional: ["interruption_sensitivity", "auto_greeting"],
    icon: "mic"
  },
  {
    id: "integrations",
    title: "Connect Your Tools",
    description: "Connect your existing tools",
    voicePrompt: "Let's connect your tools. What CRM and email do you use?",
    fields: [],
    optional: ["crm", "email_provider", "calendar", "analytics"],
    icon: "plug"
  },
  {
    id: "launch",
    title: "Ready to Launch",
    description: "You're all set!",
    voicePrompt: "You're all set! Let me show you what Genesis can do for you.",
    fields: [],
    optional: ["first_campaign", "first_workflow"],
    icon: "rocket"
  }
];

export function OnboardingWizard({ onComplete, onSkip, initialStep = 0 }: OnboardingWizardProps) {
  const [currentStep, setCurrentStep] = useState(initialStep);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [voiceState, setVoiceState] = useState<"idle" | "listening" | "speaking">("idle");
  const [isSpeaking, setIsSpeaking] = useState(false);

  const steps = STEPS;

  const currentStepData = steps[currentStep];
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === steps.length - 1;
  const progress = ((currentStep + 1) / steps.length) * 100;

  const handleVoiceToggle = () => {
    if (voiceState === "idle" || voiceState === "speaking") {
      setVoiceState("listening");
    } else if (voiceState === "listening") {
      setVoiceState("speaking");
    } else {
      setVoiceState("idle");
    }
  };

  const handleNext = () => {
    if (isLastStep) {
      onComplete(formData);
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (!isFirstStep) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    onSkip?.();
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  useEffect(() => {
    if (currentStep < steps.length) {
      const step = steps[currentStep];
      if (step.voicePrompt) {
        // Would call TTS
      }
    }
  }, [currentStep, steps]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-primary-600 to-primary-800 rounded-full"
              />
            </div>
            <span className="ml-4 text-sm font-medium text-gray-600">
              Step {currentStep + 1} of {steps.length}
            </span>
          </div>
          
          <div className="flex items-center justify-between text-sm text-gray-500">
            {steps.map((step, i) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.1 }}
                className={`flex flex-col items-center gap-1 ${i === currentStep ? 'text-primary-700' : 'text-gray-400'}`}
                aria-current={i === currentStep ? "step" : undefined}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                  i < currentStep ? 'bg-primary-600 text-white' : 
                  i === currentStep ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-400'
                }`}>
                  {i < currentStep ? <Check className="w-4 h-4" aria-hidden="true" /> : <span>{i + 1}</span>}
                </div>
                <span className="text-xs mt-1 truncate w-24 text-center">{step.title}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStepData.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-100 shadow-xl p-8">
              {/* Step Header */}
              <div className="mb-8">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-white" aria-hidden="true" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">{currentStepData.title}</h1>
                    <p className="text-gray-600">{currentStepData.description}</p>
                  </div>
                </div>

                {/* Voice Controls */}
                <div className="flex items-center gap-3 mb-8 p-4 bg-primary-50 rounded-xl">
                  <VoiceOrb 
                    state={isSpeaking ? "speaking" : voiceState === "listening" ? "listening" : "idle"}
                    className="w-14 h-14"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Voice Assistant</p>
                    <p className="text-sm text-gray-500">
                      {isSpeaking ? "Speaking..." : voiceState === "listening" ? "Listening..." : "Tap to speak"}
                    </p>
                  </div>
                  <button
                    onClick={handleVoiceToggle}
                    className={`p-2 rounded-lg transition-colors ${
                      voiceState === "listening" ? "bg-primary-100 text-primary-700" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                    aria-label={voiceState === "listening" ? "Stop listening" : "Start listening"}
                  >
                    <Mic className="w-5 h-5" />
                  </button>
                </div>

                {/* Step Fields */}
                <div className="space-y-6">
                  {currentStepData.fields.map((field, i) => (
                    <motion.div
                      key={field}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="space-y-2"
                    >
                      <label htmlFor={field} className="block text-sm font-medium text-gray-700 mb-2">
                        {field.replace(/_/g, " ")}
                        {currentStepData.fields.includes(field) && (
                          <span className="text-red-500 ml-1">*</span>
                        )}
                      </label>
                      <input
                        id={field}
                        type="text"
                        name={field}
                        value={formData[field] || ""}
                        onChange={(e) => handleInputChange(field, e.target.value)}
                        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                        placeholder={`Enter ${field.replace(/_/g, " ")}`}
                      />
                    </motion.div>
                  ))}

                  {currentStepData.optional.map((field, i) => (
                    <motion.div
                      key={`optional-${field}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: (currentStepData.fields.length + i) * 0.1 }}
                      className="space-y-2"
                    >
                      <label htmlFor={field} className="block text-sm font-medium text-gray-700 mb-2">
                        {field.replace(/_/g, " ")} <span className="text-gray-400 text-xs">(optional)</span>
                      </label>
                      <input
                        id={field}
                        type="text"
                        name={field}
                        value={formData[field] || ""}
                        onChange={(e) => handleInputChange(field, e.target.value)}
                        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                        placeholder={`Enter ${field.replace(/_/g, " ")} (optional)`}
                      />
                    </motion.div>
                  ))}

                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-100">
                  <button
                    onClick={handleBack}
                    disabled={isFirstStep}
                    className="px-6 py-3 text-gray-600 hover:text-gray-900 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Back
                  </button>

                  <div className="flex items-center gap-3">
                    {isLastStep ? (
                      <motion.button
                        onClick={handleNext}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="flex-1 px-8 py-3 bg-gradient-to-r from-primary-600 to-primary-800 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-shadow"
                      >
                        Complete Setup
                        <ArrowRight className="w-5 h-5 ml-2" />
                      </motion.button>
                    ) : (
                      <>
                        <button
                          onClick={handleSkip}
                          className="px-6 py-3 text-gray-500 hover:text-gray-700 font-medium"
                        >
                          Skip
                        </button>
                        <motion.button
                          onClick={handleNext}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="flex-1 px-8 py-3 bg-gradient-to-r from-primary-600 to-primary-800 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-shadow"
                        >
                          Next Step
                          <ChevronRight className="w-5 h-5 ml-2" />
                        </motion.button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
            </motion.div>
          </AnimatePresence>

          {/* Skip Link */}
          {!isLastStep && (
            <div className="text-center mt-6">
              <button
                onClick={handleSkip}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Skip onboarding for now
              </button>
            </div>
          )}

        </div>
      </div>
  );
}

interface StepData {
  id?: string;
  title?: string;
  description?: string;
  voicePrompt?: string;
  fields?: string[];
  optional?: string[];
  icon?: string;
}

export function OnboardingStep({ step, onNext, onBack, isFirst, isLast }: {
  step: StepData;
  onNext: () => void;
  onBack: () => void;
  isFirst: boolean;
  isLast: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3 }}
      className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-100 shadow-xl p-8"
    >
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{step.title}</h1>
            <p className="text-gray-600">{step.description}</p>
          </div>
        </div>

        <div className="space-y-6">
          {step.fields?.map((field: string, i: number) => (
            <motion.div
              key={field}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="space-y-2"
            >
              <label htmlFor={field} className="block text-sm font-medium text-gray-700 mb-2">
                {field.replace(/_/g, " ")}
                {step.fields?.includes(field) && <span className="text-red-500 ml-1">*</span>}
              </label>
              <input
                id={field}
                type="text"
                name={field}
                defaultValue=""
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder={`Enter ${field.replace(/_/g, " ")}`}
              />
            </motion.div>
          ))}

          {step.optional?.map((field: string, i: number) => (
            <motion.div
              key={field}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: (step.fields?.length ?? 0) + i * 0.1 }}
              className="space-y-2"
            >
              <label htmlFor={field} className="block text-sm font-medium text-gray-700 mb-2">
                {field.replace(/_/g, " ")} <span className="text-gray-400 text-xs">(optional)</span>
              </label>
              <input
                id={field}
                type="text"
                name={field}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder={`Enter ${field.replace(/_/g, " ")} (optional)`}
              />
            </motion.div>
          ))}
        </div>

        <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-100">
          <button
            onClick={onBack}
            disabled={isFirst}
            className="px-6 py-3 text-gray-600 hover:text-gray-900 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Back
          </button>

          <div className="flex items-center gap-3">
            {isLast ? (
              <motion.button
                onClick={onNext}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex-1 px-8 py-3 bg-gradient-to-r from-primary-600 to-primary-800 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-shadow"
              >
                Complete Setup
                <ArrowRight className="w-5 h-5 ml-2" />
              </motion.button>
            ) : (
              <>
                <button
                  onClick={() => {}}
                  className="px-6 py-3 text-gray-500 hover:text-gray-700 font-medium"
                >
                  Skip
                </button>
                <motion.button
                  onClick={onNext}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex-1 px-8 py-3 bg-gradient-to-r from-primary-600 to-primary-800 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-shadow"
                >
                  Next Step
                  <ArrowRight className="w-5 h-5 ml-2" />
                </motion.button>
              </>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function Mic({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h10m-7 0a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  );
}

function Check({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  );
}

function ArrowRight({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>
  );
}

