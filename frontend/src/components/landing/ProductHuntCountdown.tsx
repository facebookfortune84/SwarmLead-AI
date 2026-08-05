"use client";

import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  formatTargetLabel,
  getTimeLeft,
  pad,
  PRODUCT_HUNT_LAUNCH_AT,
  TimeLeft,
} from "@/lib/countdown";
import { PRODUCT_HUNT_URL } from "@/lib/launch";

function TimeUnit({ value, label }: { value: string; label: string }) {
  return (
    <div className="flex flex-col items-center">
      <div className="relative h-16 w-16 sm:h-20 sm:w-20 overflow-hidden rounded-xl bg-white/[0.06] border border-white/10 backdrop-blur-xl flex items-center justify-center shadow-lg shadow-black/20">
        <AnimatePresence mode="popLayout">
          <motion.span
            key={value}
            initial={{ y: 24, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -24, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="absolute text-3xl sm:text-4xl font-bold text-white tabular-nums bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent"
          >
            {value}
          </motion.span>
        </AnimatePresence>
      </div>
      <span className="mt-2 text-[10px] sm:text-xs font-medium uppercase tracking-widest text-white/50">
        {label}
      </span>
    </div>
  );
}

export function ProductHuntCountdown() {
  const [now, setNow] = useState<TimeLeft>(() => getTimeLeft(PRODUCT_HUNT_LAUNCH_AT));

  useEffect(() => {
    const id = setInterval(() => setNow(getTimeLeft(PRODUCT_HUNT_LAUNCH_AT)), 1000);
    return () => clearInterval(id);
  }, []);

  const targetLabel = useMemo(() => formatTargetLabel(PRODUCT_HUNT_LAUNCH_AT), []);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-indigo-950/60 via-purple-950/40 to-gray-950/60 backdrop-blur-xl">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent" />
      <div className="relative px-6 py-6 sm:px-8 text-center">
        {now.live ? (
          <div className="space-y-3">
            <p className="inline-flex items-center gap-2 rounded-full bg-emerald-500/15 border border-emerald-400/30 px-4 py-1.5 text-sm font-semibold text-emerald-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
              We are LIVE on Product Hunt
            </p>
            <h3 className="text-2xl sm:text-3xl font-bold text-white">
              Genesis Forge is launching right now
            </h3>
            <a
              href={PRODUCT_HUNT_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all"
            >
              Upvote on Product Hunt
            </a>
          </div>
        ) : (
          <>
            <p className="inline-flex items-center gap-2 rounded-full bg-indigo-500/15 border border-indigo-400/30 px-4 py-1.5 text-xs sm:text-sm font-semibold text-indigo-300">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" aria-hidden="true" />
              Launching on Product Hunt {targetLabel}
            </p>
            <h3 className="mt-4 text-xl sm:text-2xl font-bold text-white">
              Genesis Forge goes live
            </h3>
            <div className="mt-5 flex items-center justify-center gap-3 sm:gap-4">
              <TimeUnit value={String(now.days)} label="Days" />
              <span className="text-2xl sm:text-3xl font-bold text-white/30 pb-6">:</span>
              <TimeUnit value={pad(now.hours)} label="Hours" />
              <span className="text-2xl sm:text-3xl font-bold text-white/30 pb-6">:</span>
              <TimeUnit value={pad(now.minutes)} label="Minutes" />
              <span className="text-2xl sm:text-3xl font-bold text-white/30 pb-6">:</span>
              <TimeUnit value={pad(now.seconds)} label="Seconds" />
            </div>
            <p className="mt-5 text-sm text-white/60">
              Founders on launch day get{" "}
              <span className="text-white font-semibold">1 month free</span> on any plan.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
