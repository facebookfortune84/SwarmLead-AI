"use client";

import { motion } from "framer-motion";
import { Mic, Sparkles, TrendingUp, Users, Shield, Zap } from "lucide-react";

const features = [
  {
    title: "Voice-First AI Agents",
    desc: "Natural voice conversations with barge-in support. Interrupt naturally, just like talking to a human.",
    icon: Mic
  },
  {
    title: "Autonomous Business Launch",
    desc: "From idea to incorporated entity. Legal, banking, website, and first customers - fully automated.",
    icon: Zap
  },
  {
    title: "Autonomous Lead Generation",
    desc: "AI agents that discover, qualify, and engage leads 24/7. Voice-first outreach at scale.",
    icon: TrendingUp
  },
  {
    title: "Autonomous Workflows",
    desc: "Multi-agent swarms that execute complex business processes end-to-end without human intervention.",
    icon: Users
  },
  {
    title: "Constitutional Compliance",
    desc: "Built-in governance. Every agent action traceable, every dollar human-approved, every decision auditable.",
    icon: Shield
  },
  {
    title: "Voice-First Onboarding",
    desc: "Conversational setup in minutes, not hours. Talk to your AI, don't click through forms.",
    icon: Sparkles
  }
];

export function FeatureShowcase() {
  return (
    <section className="py-20 px-6 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="text-center mb-16"
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Everything You Need to{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Launch & Grow
          </span>
        </h2>
        <p className="text-xl text-white/60 max-w-2xl mx-auto">
          Genesis combines voice-first AI agents with constitutional governance to give you
          the power of an entire business operations team - without the overhead.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {features.map((feature, i) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            className="group p-8 bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] hover:border-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/10 transition-all duration-300"
          >
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
              <feature.icon className="w-7 h-7 text-white" aria-hidden="true" />
            </div>
            <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
            <p className="text-white/60 leading-relaxed">{feature.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export function SocialProof() {
  const stats = [
    { value: "15", label: "AI Agents on Staff" },
    { value: "24/7", label: "Voice Agent Coverage" },
    { value: "1", label: "Human Approval Gate" },
    { value: "0", label: "Lines of Code Required" }
  ];

  return (
    <section className="py-16 px-6 max-w-7xl mx-auto">
      <div className="bg-gradient-to-r from-indigo-900 via-purple-800 to-indigo-900 rounded-3xl p-12 md:p-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold text-white mb-2">
                {stat.value}
              </div>
              <div className="text-amber-300 font-medium">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

const testimonialThemes = [
  {
    title: "From idea to first customer",
    quote: "Speak your vision, and Genesis provisions the workspace, launches the landing page, and starts qualifying leads while you do your day job.",
  },
  {
    title: "Every action, auditable",
    quote: "Constitutional AI means nothing goes out without your approval. Every lead, every draft, every dollar is tracked and reviewable.",
  },
  {
    title: "Setup in minutes, not weeks",
    quote: "Voice-first onboarding builds your agent workforce, workflows, and company skeleton from a single spoken prompt.",
  },
];

export function Testimonials() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            What Launching with Genesis Looks Like
          </h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">
            One workspace, 15 agents, one human approval gate. No code, no
            waiting on an agency.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonialThemes.map((t, i) => (
            <motion.div
              key={t.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-8 shadow-xl shadow-black/30"
            >
              <div className="flex items-center gap-1 mb-6">
                {[...Array(5)].map((_, j) => (
                  <svg key={j} className="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <h3 className="text-white font-semibold mb-3">{t.title}</h3>
              <p className="text-white/80 leading-relaxed">&ldquo;{t.quote}&rdquo;</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function CTASection() {
  return (
    <section className="py-20 px-6 max-w-7xl mx-auto text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-gradient-to-br from-gray-950 via-indigo-950/90 to-gray-950 rounded-3xl p-12 md:p-16 border border-white/[0.06] shadow-2xl shadow-black/50"
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Ready to Launch Your Business?
        </h2>
        <p className="text-xl text-white/60 mb-10 max-w-2xl mx-auto">
          Start free, no credit card. Scale your lead pipeline with your voice.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a 
            href="/onboarding" 
            className="group relative px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all duration-300 overflow-hidden"
          >
            <span className="relative z-10">Start Free - No Credit Card</span>
            <div className="absolute inset-0 -translate-x-full group-hover:translate-x-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700" />
          </a>
          <a 
            href="/demo" 
            className="inline-flex items-center gap-2 px-8 py-4 bg-white/5 backdrop-blur-sm border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 hover:border-white/20 transition-all duration-300"
          >
            Watch Demo
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>
      </motion.div>
    </section>
  );
}

