"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { recommendPlan, PlanQuizAnswer } from "@/lib/launch";

const QUESTIONS: {
  key: keyof PlanQuizAnswer;
  question: string;
  options: { value: PlanQuizAnswer[keyof PlanQuizAnswer]; label: string }[];
}[] = [
  {
    key: "goal",
    question: "What's your biggest goal right now?",
    options: [
      { value: "launch", label: "Launch a business fast" },
      { value: "scale", label: "Scale outreach & leads" },
      { value: "automate", label: "Automate my whole operation" },
    ],
  },
  {
    key: "teamSize",
    question: "How many people run the business?",
    options: [
      { value: "solo", label: "Just me" },
      { value: "small", label: "2–10 people" },
      { value: "large", label: "10+ people" },
    ],
  },
  {
    key: "budget",
    question: "What's your monthly budget for this?",
    options: [
      { value: "free", label: "Free / under $30" },
      { value: "mid", label: "$30–$150" },
      { value: "premium", label: "$150+ — I want it all" },
    ],
  },
];

const PLAN_DETAILS = {
  starter: {
    name: "Starter",
    price: "$29/mo",
    blurb: "Perfect for solo founders validating an idea.",
    cta: "Start Starter free",
  },
  growth: {
    name: "Growth",
    price: "$99/mo",
    blurb: "Built for small teams ready to scale outreach.",
    cta: "Start Growth free",
  },
  enterprise: {
    name: "Enterprise",
    price: "$299/mo",
    blurb: "Unlimited tenants, voice runtime, agent runtime.",
    cta: "Start Enterprise free",
  },
} as const;

export function PlanFinderQuiz() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Partial<PlanQuizAnswer>>({});
  const [result, setResult] = useState<keyof typeof PLAN_DETAILS | null>(null);
  const [email, setEmail] = useState("");
  const [captured, setCaptured] = useState(false);
  const resultRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (result) resultRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [result]);

  const choose = (value: string) => {
    const q = QUESTIONS[step];
    const next = { ...answers, [q.key]: value };
    setAnswers(next);
    if (step < QUESTIONS.length - 1) {
      setStep(step + 1);
    } else {
      const rec = recommendPlan(next as PlanQuizAnswer);
      setResult(rec);
    }
  };

  const capture = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.includes("@")) return;
    try {
      const res = await fetch("/api/voice/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source: "plan_quiz", intent_score: 90 }),
      });
      if (!res.ok) throw new Error("capture failed");
      const data = await res.json();
      if (data.created === true || data.lead_id != null) setCaptured(true);
    } catch {
      /* fall through — quiz still shows the recommendation */
      setCaptured(true);
    }
  };

  const restart = () => {
    setStep(0);
    setAnswers({});
    setResult(null);
    setCaptured(false);
    setEmail("");
  };

  return (
    <section className="py-20 px-6">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-10">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Find your{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              launch plan
            </span>
          </h2>
          <p className="text-xl text-white/60">
            Three questions. One honest recommendation. No credit card.
          </p>
        </div>

        <div ref={resultRef} className="bg-white/[0.03] backdrop-blur-xl rounded-3xl border border-white/10 p-8">
          {!result ? (
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-xs font-semibold uppercase tracking-widest text-white/50">
                  Question {step + 1} of {QUESTIONS.length}
                </span>
                <div className="flex gap-1.5">
                  {QUESTIONS.map((_, i) => (
                    <span
                      key={i}
                      className={`w-8 h-1.5 rounded-full transition-colors ${
                        i <= step ? "bg-indigo-500" : "bg-white/10"
                      }`}
                      aria-hidden="true"
                    />
                  ))}
                </div>
              </div>
              <motion.div
                key={step}
                initial={{ opacity: 0, x: 24 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <h3 className="text-2xl font-bold text-white mb-6">
                  {QUESTIONS[step].question}
                </h3>
                <div className="grid gap-3">
                  {QUESTIONS[step].options.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => choose(opt.value)}
                      className="text-left px-6 py-4 rounded-2xl bg-white/5 border border-white/10 hover:border-indigo-500/40 hover:bg-indigo-500/10 transition-all text-white font-medium"
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </motion.div>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center"
            >
              <p className="inline-flex items-center gap-2 rounded-full bg-emerald-500/15 border border-emerald-400/30 px-4 py-1.5 text-xs font-semibold text-emerald-300 mb-5">
                Your recommendation
              </p>
              <h3 className="text-3xl font-bold text-white mb-2">
                Genesis {PLAN_DETAILS[result].name}
              </h3>
              <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-400 mb-3">
                {PLAN_DETAILS[result].price}
              </p>
              <p className="text-white/60 mb-6">{PLAN_DETAILS[result].blurb}</p>

              {!captured ? (
                <form onSubmit={capture} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto mb-4">
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@company.com"
                    className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/40 focus:outline-none focus:border-indigo-500/40"
                    aria-label="Email address"
                  />
                  <button
                    type="submit"
                    className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all"
                  >
                    Unlock plan
                  </button>
                </form>
              ) : (
                <p className="text-sm text-emerald-300 mb-4">
                  Saved! We'll send your setup steps and the 1-month-free code.
                </p>
              )}
              <div className="flex items-center justify-center gap-4">
                <button
                  onClick={restart}
                  className="text-sm text-white/50 hover:text-white transition-colors"
                >
                  ← Retake quiz
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </section>
  );
}
