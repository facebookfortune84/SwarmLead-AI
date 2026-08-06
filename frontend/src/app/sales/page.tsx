"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Target, TrendingUp, CheckCircle2, Briefcase } from "lucide-react";
import {
  usePipelineSnapshot,
  useSalesForecast,
  useSalesDeals,
} from "@/hooks/use-sales";
import { formatCents, formatCentsCents, percent, stageLabel } from "@/lib/money";

const STAGE_ORDER = [
  "qualified",
  "discovery",
  "engaged",
  "quoted",
  "closed_won",
  "closed_lost",
];

const STAGE_COLORS: Record<string, string> = {
  qualified: "text-blue-400",
  discovery: "text-cyan-400",
  engaged: "text-amber-400",
  quoted: "text-violet-400",
  closed_won: "text-emerald-400",
  closed_lost: "text-rose-400",
};

export default function SalesPage() {
  const { data: pipeline, isLoading } = usePipelineSnapshot();
  const { data: forecast } = useSalesForecast();
  const { data: deals } = useSalesDeals();

  const stages = pipeline?.stages ?? [];

  return (
    <AppShell>
      <div className="space-y-8">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white">AI Sales Pipeline</h1>
          <p className="text-white/50 mt-1">
            Your SDR and Closer agents qualify leads, move deals, and quote plans —
            all human-gated.
          </p>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            {
              label: "Open Deals",
              value: pipeline?.open_deals ?? 0,
              icon: Briefcase,
              color: "text-blue-400",
            },
            {
              label: "Weighted Pipeline (mo)",
              value: formatCents(pipeline?.weighted_pipeline_cents ?? 0),
              icon: TrendingUp,
              color: "text-amber-400",
            },
            {
              label: "Closed-Won MRR",
              value: formatCents(forecast?.closed_won_mrr_cents ?? 0),
              icon: CheckCircle2,
              color: "text-emerald-400",
            },
            {
              label: "Annual Contracts",
              value: formatCents(forecast?.annual_contract_cents ?? 0),
              icon: Target,
              color: "text-purple-400",
            },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="rounded-2xl bg-white/[0.03] backdrop-blur-xl border border-white/[0.06] p-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-white/50">{stat.label}</div>
                    <div className="text-2xl font-bold text-white mt-1">{stat.value}</div>
                  </div>
                  <Icon className={`w-8 h-8 ${stat.color}`} />
                </div>
              </motion.div>
            );
          })}
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-1 bg-white/[0.03] backdrop-blur-xl border-white/[0.06] p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Stage Breakdown</h2>
            {isLoading && <div className="text-white/50 text-sm">Loading pipeline…</div>}
            <div className="space-y-4">
              {stages.map((stage) => (
                <div key={stage.stage}>
                  <div className="flex items-center justify-between text-sm">
                    <span className={`font-medium ${STAGE_COLORS[stage.stage] ?? "text-white/70"}`}>
                      {stageLabel(stage.stage)}
                    </span>
                    <span className="text-white/60">{stage.count}</span>
                  </div>
                  <div className="mt-1.5 h-2 rounded-full bg-white/5 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                      style={{
                        width: `${Math.min(100, (stage.count / Math.max(pipeline?.total_deals ?? 1, 1)) * 100)}%`,
                      }}
                    />
                  </div>
                  <div className="mt-1 text-xs text-white/40">
                    {formatCentsCents(stage.weighted_value_cents)} · {percent(stage.probability)}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="lg:col-span-2 bg-white/[0.03] backdrop-blur-xl border-white/[0.06] p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">Deals</h2>
              <Badge variant="outline">SDR + Closer agents</Badge>
            </div>
            {!deals?.length ? (
              <div className="text-white/50 text-sm py-8 text-center">
                No deals yet — the SDR agent creates them from discovered leads.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-white/40 border-b border-white/10">
                      <th className="pb-2 font-medium">Email</th>
                      <th className="pb-2 font-medium">Stage</th>
                      <th className="pb-2 font-medium">Value</th>
                      <th className="pb-2 font-medium">Prob.</th>
                      <th className="pb-2 font-medium">Owner</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(deals ?? []).map((deal) => (
                      <tr key={deal.id} className="border-b border-white/5">
                        <td className="py-2.5 text-white/80">{deal.email}</td>
                        <td className="py-2.5">
                          <Badge variant="outline" className={STAGE_COLORS[deal.stage]}>
                            {stageLabel(deal.stage)}
                          </Badge>
                        </td>
                        <td className="py-2.5 text-white/80">{formatCents(deal.amount_cents)}/mo</td>
                        <td className="py-2.5 text-white/60">{percent(deal.probability)}</td>
                        <td className="py-2.5 text-white/60">{deal.owner_agent ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        <div className="flex gap-4">
          <Button
            className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500"
            onClick={() => (window.location.href = "/revenue")}
          >
            View Revenue Dashboard
          </Button>
        </div>
      </div>
    </AppShell>
  );
}
