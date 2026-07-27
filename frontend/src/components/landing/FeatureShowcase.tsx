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
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Everything You Need to <span className="text-primary-700">Launch & Grow</span>
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
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
            className="group p-8 bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-xl transition-all duration-300"
          >
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
              <feature.icon className="w-7 h-7 text-white" aria-hidden="true" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
            <p className="text-gray-600 leading-relaxed">{feature.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export function SocialProof() {
  const stats = [
    { value: "10x", label: "Faster Launch" },
    { value: "85%", label: "Lead Conversion" },
    { value: "3min", label: "Avg Setup Time" },
    { value: "99.9%", label: "Uptime SLA" }
  ];

  return (
    <section className="py-16 px-6 max-w-7xl mx-auto">
      <div className="bg-gradient-to-r from-primary-900 via-primary-800 to-primary-900 rounded-3xl p-12 md:p-16">
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
              <div className="text-gold-300 font-medium">{stat.label}</div>
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
      >
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Ready to Launch Your Business?
        </h2>
        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
          Join 10,000+ founders who launched with Genesis. Start free, scale infinitely.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a 
            href="/onboarding" 
            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-primary-700 to-primary-900 text-white font-semibold rounded-xl hover:from-primary-800 hover:to-primary-900 shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <span className="relative z-10">Start Free - No Credit Card</span>
          </a>
          <a 
            href="/demo" 
            className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300"
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

