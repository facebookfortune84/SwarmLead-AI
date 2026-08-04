"use client";

import { motion } from "framer-motion";
import { PRODUCT_HUNT_URL } from "@/lib/launch";

const EVENTS = [
  "A founder just launched their agency with Genesis",
  "Voice agent qualified 12 leads overnight",
  "New: full-duplex barge-in — interrupt mid-sentence",
  "Growth plan founders shipped in under 3 minutes",
  "15 agents now run outreach, SEO & follow-ups",
  "A solo founder closed her first client on day 1",
];

export function LiveActivityTicker() {
  const row = [...EVENTS, ...EVENTS];
  return (
    <section className="relative py-10 overflow-hidden border-y border-white/5 bg-white/[0.02]">
      <p className="text-center text-xs font-semibold uppercase tracking-widest text-white/40 mb-6">
        Live from the launch
      </p>
      <div className="relative flex overflow-hidden" aria-hidden="true">
        <motion.div
          className="flex shrink-0 gap-10 pr-10 whitespace-nowrap"
          animate={{ x: ["0%", "-50%"] }}
          transition={{ duration: 40, ease: "linear", repeat: Infinity }}
        >
          {row.map((event, i) => (
            <span key={i} className="inline-flex items-center gap-2.5 text-sm text-white/60">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              {event}
            </span>
          ))}
        </motion.div>
      </div>
      <div className="mt-6 text-center">
        <a
          href={PRODUCT_HUNT_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm font-semibold text-indigo-300 hover:text-indigo-200 transition-colors"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M13.604 8.4h-3.405V12h3.405c.995 0 1.801-.806 1.801-1.801 0-.993-.805-1.799-1.801-1.799zM12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zm1.604 14.4h-3.405V18H7.801V6h5.804c2.319 0 4.2 1.88 4.2 4.2 0 2.32-1.881 4.2-4.2 4.2z" />
          </svg>
          Upvote Genesis Forge on Product Hunt
        </a>
      </div>
    </section>
  );
}
