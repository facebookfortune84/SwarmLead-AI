"use client";

import { motion } from "framer-motion";
import { PRODUCT_HUNT_URL, LAUNCH_COPY } from "@/lib/launch";
import { currentOrigin } from "@/lib/site";

const INTEGRATIONS = [
  "Stripe",
  "ElevenLabs",
  "OpenAI",
  "Ollama",
  "PostgreSQL",
  "Redis",
  "Docker",
  "Kubernetes",
  "Next.js",
  "FastAPI",
];

export function IntegrationsStrip() {
  return (
    <section className="py-14 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <p className="text-xs font-semibold uppercase tracking-widest text-white/40 mb-8">
          Runs on the stack you already trust
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          {INTEGRATIONS.map((name, i) => (
            <motion.span
              key={name}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="px-5 py-2.5 rounded-full bg-white/[0.04] border border-white/10 text-sm font-medium text-white/70"
            >
              {name}
            </motion.span>
          ))}
        </div>
      </div>
    </section>
  );
}

export function ReferralBanner() {
  return (
    <section className="py-16 px-6">
      <div className="max-w-4xl mx-auto rounded-3xl border border-white/10 bg-gradient-to-br from-indigo-950/60 via-purple-950/40 to-gray-950/60 backdrop-blur-xl p-10 text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent" />
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative"
        >
          <p className="inline-flex items-center gap-2 rounded-full bg-indigo-500/15 border border-indigo-400/30 px-4 py-1.5 text-xs font-semibold text-indigo-300 mb-6">
            Referral program — live now
          </p>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Launch with a friend. Both of you win.
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto mb-8">
            Refer a founder and you get {LAUNCH_COPY.referralCredit}. They get{" "}
            {LAUNCH_COPY.referralDiscount}. Every sign-up you send our way puts
            you closer to free.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <a
              href="/onboarding"
              className="px-8 py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all"
            >
              Get my referral link
            </a>
            <a
              href={PRODUCT_HUNT_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-3.5 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-all"
            >
              See the launch on Product Hunt
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export function LaunchPromoBar() {
  return (
    <motion.div
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.4, type: "spring", damping: 20 }}
      className="relative z-30 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 px-4 py-2.5 text-center text-sm"
    >
      <span className="text-white/90 font-medium">
        🔥 Launch week: use code{" "}
        <span className="font-bold text-white bg-white/20 rounded-md px-2 py-0.5">
          {LAUNCH_COPY.promoCode}
        </span>{" "}
        for {LAUNCH_COPY.promoOffer}
      </span>{" "}
      <a
        href={currentOrigin()}
        className="ml-2 inline-block underline underline-offset-2 text-white font-semibold hover:text-white/80 transition-colors"
      >
        Claim now →
      </a>
    </motion.div>
  );
}
