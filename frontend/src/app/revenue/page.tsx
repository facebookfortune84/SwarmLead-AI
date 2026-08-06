"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";
import {
  DollarSign,
  TrendingUp,
  Receipt,
  AlertTriangle,
} from "lucide-react";
import { useRevenueSummary, useChurnReport, type ChurnReport } from "@/hooks/use-revenue";
import { formatCents, percent, stageLabel } from "@/lib/money";

function ChurnList({ deals }: { deals: ChurnReport["risk"]["at_risk_deals"] }) {
  return (
    <div className="space-y-2">
      {deals.map((deal) => (
        <div
          key={deal.deal_id}
          className="flex items-center justify-between rounded-xl bg-white/5 border border-white/5 px-4 py-3 text-sm"
        >
          <div>
            <div className="text-white/80">{deal.email}</div>
            <div className="text-white/40 text-xs">
              {stageLabel(deal.stage)} · silent {Math.round(deal.days_inactive)}d
            </div>
          </div>
          <Badge variant="outline" className="text-rose-400">At risk</Badge>
        </div>
      ))}
    </div>
  );
}

export default function RevenuePage() {
  const { data: summary } = useRevenueSummary();
  const { data: churn } = useChurnReport();

  const tierNames: Record<string, string> = {
    starter: "Starter",
    growth: "Growth",
    enterprise: "Enterprise",
  };

  return (
    <AppShell>
      <div className="space-y-8">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white">Revenue Radar</h1>
          <p className="text-white/50 mt-1">
            MRR, ARR, LTV and churn — computed from your pipeline and approved quotes.
          </p>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            {
              label: "Monthly Recurring",
              value: formatCents(summary?.mrr_cents ?? 0),
              icon: DollarSign,
              color: "text-emerald-400",
            },
            {
              label: "Annualized (ARR)",
              value: formatCents(summary?.arr_cents ?? 0),
              icon: TrendingUp,
              color: "text-blue-400",
            },
            {
              label: "Closed-Won Deals",
              value: summary?.closed_won_count ?? 0,
              icon: Receipt,
              color: "text-purple-400",
            },
            {
              label: "Quotes Approved",
              value: summary?.quotes_approved ?? 0,
              icon: TrendingUp,
              color: "text-amber-400",
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

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="bg-white/[0.03] backdrop-blur-xl border-white/[0.06] p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Tier Mix</h2>
            <div className="space-y-4">
              {Object.entries(summary?.tier_mix ?? {}).map(([tier, mix]) => {
                const total = summary?.mrr_cents ?? 1;
                const share = total > 0 ? Math.min(100, (mix.mrr_cents / total) * 100) : 0;
                return (
                  <div key={tier}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-white/80">{tierNames[tier] ?? tier}</span>
                      <span className="text-white/60">
                        {mix.count} deal{mix.count === 1 ? "" : "s"} · {formatCents(mix.mrr_cents)}
                      </span>
                    </div>
                    <div className="mt-1.5 h-2 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-500"
                        style={{ width: `${share}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-6 pt-4 border-t border-white/10">
              <h3 className="text-sm font-semibold text-white mb-3">Lifetime Value</h3>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-white/50">LTV (est.)</div>
                  <div className="text-xl font-bold text-white">
                    {formatCents(churn?.ltv.ltv_cents ?? 0)}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-white/50">Avg lifetime</div>
                  <div className="text-xl font-bold text-white">
                    {churn?.ltv.avg_customer_lifetime_months ?? "—"} months
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card className="bg-white/[0.03] backdrop-blur-xl border-white/[0.06] p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Churn Radar</h2>
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-white/50">Risk rate</div>
              <Badge
                variant={churn && churn.risk.risk_rate > 0 ? "default" : "outline"}
                className={churn && churn.risk.risk_rate > 0 ? "" : "text-emerald-400"}
              >
                {churn ? percent(churn.risk.risk_rate) : "—"}
              </Badge>
            </div>

            {!churn?.risk.at_risk_deals.length ? (
              <div className="flex items-center gap-2 text-sm text-emerald-400/80 py-6">
                <AlertTriangle className="w-4 h-4" />
                No quiet deals — pipeline is healthy.
              </div>
            ) : (
              <ChurnList deals={churn.risk.at_risk_deals} />
            )}

            <div className="mt-6 pt-4 border-t border-white/10">
              <h3 className="text-sm font-semibold text-white mb-3">12-Month Retention</h3>
              <div className="flex items-end gap-1 h-16">
                {(churn?.retention_curve ?? []).slice(0, 12).map(
                  (point: ChurnReport["retention_curve"][number]) => (
                  <div
                    key={point.month}
                    className="flex-1 rounded-t bg-gradient-to-t from-emerald-600/60 to-teal-400/80"
                    style={{ height: `${point.retention_rate * 100}%` }}
                    title={`Month ${point.month}: ${percent(point.retention_rate)}`}
                  />
                ))}
              </div>
              <div className="mt-2 text-xs text-white/40">
                Cohort retention at {churn ? percent(churn.ltv.churn_rate) : "—"} monthly churn
              </div>
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}