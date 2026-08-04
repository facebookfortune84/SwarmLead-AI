"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { calculateROI, clampHours, clampLeads } from "@/lib/roi";

export function ROICalculator() {
  const [leadsPerMonth, setLeadsPerMonth] = useState(200);
  const [teamHours, setTeamHours] = useState(80);

  const output = useMemo(() => calculateROI({ leadsPerMonth, teamHours }), [leadsPerMonth, teamHours]);

  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(Math.max(0, n));

  return (
    <section className="py-20 px-6 max-w-7xl mx-auto" id="roi-calculator">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-12"
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Calculate Your{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Monthly Savings
          </span>
        </h2>
        <p className="text-xl text-white/60 max-w-2xl mx-auto">
          See what Genesis Forge saves you in acquisition cost and team hours —
          before you spend a cent.
        </p>
      </motion.div>

      <div className="max-w-4xl mx-auto bg-white/[0.03] backdrop-blur-xl rounded-3xl border border-white/[0.06] p-8 md:p-12">
        <div className="grid md:grid-cols-2 gap-10">
          <div className="space-y-10">
            <div>
              <div className="flex items-center justify-between mb-3">
                <label htmlFor="roi-leads" className="text-white font-medium">
                  Leads per month
                </label>
                <span className="text-indigo-300 font-semibold">{leadsPerMonth}</span>
              </div>
              <input
                id="roi-leads"
                type="range"
                min={50}
                max={2000}
                step={50}
                value={leadsPerMonth}
                onChange={(e) => setLeadsPerMonth(Number(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-3">
                <label htmlFor="roi-hours" className="text-white font-medium">
                  Hours you spend on lead work / week
                </label>
                <span className="text-indigo-300 font-semibold">{teamHours}h</span>
              </div>
              <input
                id="roi-hours"
                type="range"
                min={5}
                max={160}
                step={5}
                value={teamHours}
                onChange={(e) => setTeamHours(Number(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-white/5 rounded-xl p-4">
                <div className="text-white/50">Manual labor cost</div>
                <div className="text-white font-bold text-lg">{fmt(output.manualCost)}/mo</div>
              </div>
              <div className="bg-white/5 rounded-xl p-4">
                <div className="text-white/50">Cheaper acquisition</div>
                <div className="text-white font-bold text-lg">{fmt(output.leadCostSaved)}/mo</div>
              </div>
            </div>
          </div>

          <div className="flex flex-col items-center justify-center bg-gradient-to-br from-indigo-600/20 to-purple-600/10 rounded-2xl border border-indigo-500/20 p-8 text-center">
            <div className="text-white/50 text-sm uppercase tracking-widest">Estimated savings</div>
            <div className="mt-2 text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              {fmt(output.monthlySavings)}
            </div>
            <div className="text-white/60 mt-1">per month</div>
            <div className="mt-6 text-lg text-white">
              <span className="font-semibold">{fmt(output.yearlySavings)}</span>{" "}
              <span className="text-white/50">per year</span>
            </div>
            <Link
              href="/onboarding"
              className="mt-8 px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all"
            >
              Start Free — See It Yourself
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
