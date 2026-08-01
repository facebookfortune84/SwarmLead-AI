"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic, Sparkles, Rocket, Shield, Scale, FileCheck, Globe, ChevronDown,
  Lock, HeartHandshake, Workflow as WorkflowIcon, CheckCircle2, ArrowRight,
} from "lucide-react";
import Link from "next/link";

// ─────────────────────────────────────────────────────────────────────────────
// How It Works
// ─────────────────────────────────────────────────────────────────────────────

const STEPS = [
  {
    icon: Mic,
    title: "Speak Your Vision",
    desc: "Tell Genesis about your business idea in natural conversation. The voice agent understands your industry, audience, and goals instantly.",
  },
  {
    icon: Sparkles,
    title: "AI Builds Everything",
    desc: "A swarm of specialized agents configures your CRM, workflows, voice agent personality, and compliance guardrails — from your words alone.",
  },
  {
    icon: Rocket,
    title: "Launch in Minutes",
    desc: "Go live with a ready-to-serve business: leads flowing in, voice agent answering 24/7, and growth playbooks already running.",
  },
];

export function HowItWorks() {
  return (
    <section className="py-20 px-6 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-16"
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          From Idea to{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Operating Business
          </span>{" "}
          in Three Steps
        </h2>
        <p className="text-xl text-white/60 max-w-2xl mx-auto">
          No forms. No setup. No technical skills required. Just talk to Genesis.
        </p>
      </motion.div>

      <div className="relative grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="hidden md:block absolute top-14 left-[16%] right-[16%] h-px bg-gradient-to-r from-indigo-500/40 via-purple-500/40 to-pink-500/40" />
        {STEPS.map((step, i) => {
          const Icon = step.icon;
          return (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.12 }}
              className="relative text-center"
            >
              <div className="relative z-10 mx-auto w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 mb-5">
                <Icon className="w-7 h-7 text-white" />
              </div>
              <div className="text-xs font-bold text-indigo-300/70 mb-2">STEP 0{i + 1}</div>
              <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
              <p className="text-white/60 leading-relaxed max-w-xs mx-auto">{step.desc}</p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Security & Compliance
// ─────────────────────────────────────────────────────────────────────────────

const TRUST = [
  {
    icon: Shield,
    title: "Constitutional Guardrails",
    desc: "Every agent action is constrained by an explicit constitution — no surprises, ever.",
  },
  {
    icon: Scale,
    title: "Human-Approved Spend",
    desc: "Every dollar is pre-authorized and traceable. The AI never spends without consent.",
  },
  {
    icon: FileCheck,
    title: "Full Audit Trails",
    desc: "Complete, immutable records of every decision, action, and outcome in your business.",
  },
  {
    icon: Lock,
    title: "Sovereign-First Storage",
    desc: "Your data stays in your control — optional local storage keeps everything on your infrastructure.",
  },
];

export function SecurityTrust() {
  return (
    <section className="py-20 px-6 bg-gradient-to-b from-transparent via-indigo-950/30 to-transparent">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Built for{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400">
              Trust & Accountability
            </span>
          </h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">
            Autonomous doesn&apos;t mean unchecked. Genesis runs on a constitution that keeps humans in control.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {TRUST.map((item, i) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="p-6 bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] hover:border-emerald-500/30 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-white/60 leading-relaxed">{item.desc}</p>
              </motion.div>
            );
          })}
        </div>

        <div className="mt-12 flex flex-wrap justify-center gap-3">
          {["SOC 2 Ready", "GDPR Friendly", "Stripe Verified", "256-bit Encryption", "Zero Vendor Lock-In", "Open Source"].map((badge) => (
            <span key={badge} className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-white/60 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              {badge}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Feature Comparison
// ─────────────────────────────────────────────────────────────────────────────

const COMPARISON = [
  { feature: "Voice-first AI onboarding", genesis: true, traditional: false },
  { feature: "Autonomous lead generation", genesis: true, traditional: false },
  { feature: "Multi-agent workflow swarm", genesis: true, traditional: false },
  { feature: "Constitutional governance", genesis: true, traditional: false },
  { feature: "24/7 voice agent", genesis: true, traditional: false },
  { feature: "Setup time", genesis: true, traditional: false },
];

export function ComparisonSection() {
  return (
    <section className="py-20 px-6 max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-12"
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Genesis vs.{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-rose-400 to-orange-400">
            Everything Else
          </span>
        </h2>
      </motion.div>

      <div className="rounded-2xl overflow-hidden border border-white/[0.06] bg-white/[0.02] backdrop-blur-xl">
        <div className="grid grid-cols-3 px-6 py-4 bg-white/[0.04] border-b border-white/[0.06] text-sm font-semibold">
          <div className="text-white/50">Capability</div>
          <div className="text-center text-white">Genesis</div>
          <div className="text-center text-white/50">Traditional SaaS</div>
        </div>
        {COMPARISON.map((row, i) => (
          <div
            key={row.feature}
            className={`grid grid-cols-3 px-6 py-4 text-sm items-center ${i % 2 ? "bg-white/[0.02]" : ""}`}
          >
            <div className="text-white/80">{row.feature}</div>
            <div className="flex justify-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="flex justify-center">
              {row.traditional ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              ) : (
                <span className="w-5 h-5 rounded-full bg-white/10 text-white/40 flex items-center justify-center text-xs">✕</span>
              )}
            </div>
          </div>
        ))}
        <div className="grid grid-cols-3 px-6 py-5 border-t border-white/[0.06] text-sm items-center">
          <div className="text-white/80 font-medium">Time to first customer</div>
          <div className="text-center font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">~48 hours</div>
          <div className="text-center text-white/40">Months</div>
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// FAQ
// ─────────────────────────────────────────────────────────────────────────────

const FAQS = [
  {
    q: "Do I need any technical skills?",
    a: "No. You describe your business to the voice agent and Genesis configures everything — CRM, workflows, voice agent, and compliance — automatically.",
  },
  {
    q: "How does the AI handle my money?",
    a: "Every dollar of spend is pre-authorized and human-approved. The constitutional AI framework requires explicit consent before any transaction.",
  },
  {
    q: "Is my business data safe?",
    a: "Yes. Genesis supports sovereign-first storage, meaning your data can stay on your own infrastructure. Full audit trails are kept for every action.",
  },
  {
    q: "Can I really launch in minutes?",
    a: "Yes. Most founders go from their first conversation to a live, lead-generating business in under an hour — with a working voice agent answering 24/7.",
  },
  {
    q: "What happens after launch?",
    a: "The agent swarm keeps working: qualifying leads, following up, publishing SEO content, and routing hot prospects to you — around the clock.",
  },
];

export function FAQSection() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section className="py-20 px-6 max-w-3xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-12"
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Frequently Asked Questions</h2>
      </motion.div>
      <div className="space-y-3">
        {FAQS.map((faq, i) => (
          <motion.div
            key={faq.q}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.05 }}
            className="rounded-xl border border-white/[0.06] bg-white/[0.03] backdrop-blur-xl overflow-hidden"
          >
            <button
              onClick={() => setOpen(open === i ? null : i)}
              className="w-full flex items-center justify-between px-6 py-5 text-left"
              aria-expanded={open === i}
            >
              <span className="font-medium text-white pr-6">{faq.q}</span>
              <ChevronDown
                className={`w-5 h-5 text-white/40 shrink-0 transition-transform ${open === i ? "rotate-180" : ""}`}
              />
            </button>
            <AnimatePresence initial={false}>
              {open === i && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <p className="px-6 pb-5 text-sm text-white/60 leading-relaxed">{faq.a}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Final CTA + Footer
// ─────────────────────────────────────────────────────────────────────────────

export function FinalCTA() {
  return (
    <section className="py-24 px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        className="max-w-5xl mx-auto relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800 p-12 md:p-20 text-center shadow-2xl shadow-indigo-500/30"
      >
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white/40 via-transparent to-transparent" />
        <div className="relative z-10">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center mb-8">
            <HeartHandshake className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6 tracking-tight">
            Your Business Awaits.
            <br />
            Just Start Talking.
          </h2>
          <p className="text-xl text-white/80 max-w-2xl mx-auto mb-12">
            Launch your dream business with your voice. Free to start, no credit card required.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/onboarding"
              className="group inline-flex items-center justify-center gap-2 px-10 py-4 bg-white text-indigo-700 font-semibold rounded-xl hover:bg-indigo-50 shadow-xl transition-all duration-300 text-lg"
            >
              Start Free Now
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/demo"
              className="inline-flex items-center justify-center px-10 py-4 bg-white/10 backdrop-blur-sm border border-white/30 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300 text-lg"
            >
              See the Demo
            </Link>
          </div>
        </div>
      </motion.div>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="py-16 px-6 border-t border-white/[0.06] bg-black/20">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-10">
        <div className="md:col-span-1">
          <div className="flex items-center gap-2 mb-4">
            <Globe className="w-5 h-5 text-indigo-400" />
            <span className="text-white font-bold">Genesis Forge</span>
          </div>
          <p className="text-sm text-white/50 leading-relaxed">
            The first autonomous business launch platform powered by constitutional voice AI.
          </p>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white mb-4">Product</h4>
          <ul className="space-y-2 text-sm text-white/50">
            <li><Link href="/demo" className="hover:text-white transition-colors">Interactive Demo</Link></li>
            <li><Link href="/onboarding" className="hover:text-white transition-colors">Onboarding</Link></li>
            <li><Link href="/login" className="hover:text-white transition-colors">Sign In</Link></li>
            <li><Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white mb-4">Capabilities</h4>
          <ul className="space-y-2 text-sm text-white/50">
            <li className="flex items-center gap-2"><WorkflowIcon className="w-3.5 h-3.5 text-indigo-400" /> AI Workflows</li>
            <li className="flex items-center gap-2"><Mic className="w-3.5 h-3.5 text-indigo-400" /> Voice Agents</li>
            <li className="flex items-center gap-2"><Shield className="w-3.5 h-3.5 text-indigo-400" /> Constitutional AI</li>
            <li className="flex items-center gap-2"><Rocket className="w-3.5 h-3.5 text-indigo-400" /> Business Launch</li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white mb-4">Legal</h4>
          <ul className="space-y-2 text-sm text-white/50">
            <li><span className="hover:text-white transition-colors cursor-pointer">Privacy Policy</span></li>
            <li><span className="hover:text-white transition-colors cursor-pointer">Terms of Service</span></li>
            <li><span className="hover:text-white transition-colors cursor-pointer">Security</span></li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto mt-12 pt-6 border-t border-white/[0.06] flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-xs text-white/40">© {new Date().getFullYear()} Genesis Forge. All rights reserved.</p>
        <p className="text-xs text-white/40 flex items-center gap-1.5">
          <Lock className="w-3.5 h-3.5" /> Sovereign-friendly · Open source · Built for founders
        </p>
      </div>
    </footer>
  );
}
