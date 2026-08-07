"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { PRODUCT_HUNT_URL } from "@/lib/launch";

interface LaunchActivity {
  launch_week: boolean;
  leads_since_launch: number;
  leads_by_source: Record<string, number>;
  high_intent_leads: number;
  growth_cycles: number;
  approval_pending: number;
}

const FALLBACK_EVENTS = [
  "19 agents run outreach, SEO & follow-ups behind one approval gate",
  "Full-duplex barge-in — interrupt the voice agent mid-sentence",
  "A business skeleton from a single spoken prompt",
  "Every lead qualified, every send human-approved",
  "Launch week: 1 month free on any plan",
];

function activityMoments(a: LaunchActivity): string[] {
  const moments: string[] = [];
  if (a.launch_week) moments.push(`Launch week is live — ${a.leads_since_launch} leads captured so far`);
  if (a.high_intent_leads > 0) moments.push(`${a.high_intent_leads} high-intent leads waiting in your queue`);
  const bySource = Object.entries(a.leads_by_source);
  if (bySource.length > 0) {
    const top = bySource.sort((x, y) => y[1] - x[1])[0];
    moments.push(`Most leads coming from ${top[0] === "voice" ? "the voice agent" : top[0].replace(/_/g, " ")} — ${top[1]}`);
  }
  if (a.growth_cycles > 0) moments.push(`${a.growth_cycles} growth cycles run since launch`);
  if (a.approval_pending > 0) moments.push(`${a.approval_pending} actions awaiting your approval`);
  return moments.length >= 3 ? moments : [...moments, ...FALLBACK_EVENTS].slice(0, 6);
}

export function LiveActivityTicker() {
  const [events, setEvents] = useState<string[]>(FALLBACK_EVENTS);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 8000);
    fetch("/api/launch/activity", { signal: controller.signal })
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error("not ok"))))
      .then((data: LaunchActivity) => {
        if (!cancelled) setEvents(activityMoments(data));
      })
      .catch(() => {
        /* keep the honest fallback copy */
      })
      .finally(() => window.clearTimeout(timer));
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, []);

  const row = [...events, ...events];
  return (
    <section className="relative py-10 overflow-hidden border-y border-white/5 bg-white/[0.02]">
      <p className="text-center text-xs font-semibold uppercase tracking-widest text-white/40 mb-6">
        Launch-week activity
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
