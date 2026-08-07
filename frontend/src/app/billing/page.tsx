"use client";

import Image from "next/image";
import { useState } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateCheckoutSession } from "@/hooks/use-create-checkout-session";
import { useBillingTiers, useUsageInvoice } from "@/hooks/use-revenue";
import { formatCentsCents, annualSavings } from "@/lib/money";

interface Plan {
  name: string;
  monthlyCents: number;
  image: string;
  description: string;
  features: string[];
  popular?: boolean;
}

const PLANS: Plan[] = [
  {
    name: "Starter",
    monthlyCents: 2900,
    image: "/stripe_image_genesis_starter.png",
    description: "For small teams getting started with lead generation.",
    features: ["CRM & Lead Management", "Workflow Engine", "Single Tenant", "Basic Outreach", "Email Support"],
  },
  {
    name: "Growth",
    monthlyCents: 9900,
    image: "/stripe_image_genesis_growth.png",
    description: "Production-ready outreach and workflow automation.",
    features: ["Everything in Starter", "Advanced Workflows", "Multi-Tenant", "Campaign Outreach", "Reporting & Analytics", "Priority Support"],
    popular: true,
  },
  {
    name: "Enterprise",
    monthlyCents: 29900,
    image: "/stripe_image_genesis_enterprise.png",
    description: "Large scale automation with AI agent runtime support.",
    features: ["Everything in Growth", "Unlimited Tenants", "Voice AI Runtime", "Custom Agent Development", "Dedicated Account Manager", "99.99% Uptime SLA"],
  },
];

export default function BillingPage() {
  const checkout = useCreateCheckoutSession();
  const { data: tiers } = useBillingTiers();
  const [annual, setAnnual] = useState(false);
  const [usageUnits, setUsageUnits] = useState<number | null>(null);
  const usage = useUsageInvoice(usageUnits ?? 0, 50);

  const multiplier = tiers?.annual_multiplier ?? 10;

  const handleCheckout = async (plan: Plan) => {
    try {
      const session = await checkout.mutateAsync({
        product_name: plan.name,
        amount_cents: plan.monthlyCents,
        billing: annual ? "annual" : "monthly",
      });
      if (session?.url) {
        window.location.assign(session.url);
      }
    } catch (error) {
      console.error("Checkout failed", error);
    }
  };

  return (
    <AppShell>
      <div className="space-y-8">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white">Billing & Plans</h1>
          <p className="text-white/50 mt-1">
            Choose the plan that fits your business. Upgrade or cancel anytime.
            Annual billing locks in 2 months free.
          </p>
        </motion.div>

        <div className="inline-flex items-center gap-3 rounded-full bg-white/5 border border-white/10 p-1.5">
          <button
            onClick={() => setAnnual(false)}
            className={`px-5 py-2 rounded-full text-sm font-semibold transition-all ${
              !annual ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white" : "text-white/60 hover:text-white"
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setAnnual(true)}
            className={`px-5 py-2 rounded-full text-sm font-semibold transition-all ${
              annual ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white" : "text-white/60 hover:text-white"
            }`}
          >
            Annual{" "}
            <span className={annual ? "text-emerald-300" : "text-emerald-400/80"}>2 mo free</span>
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {PLANS.map((plan, i) => {
            const monthly = plan.monthlyCents / 100;
            const display = annual ? Math.round((monthly * multiplier) / 12) : monthly;
            const savings = annualSavings(monthly, multiplier);
            return (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="relative bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-8 flex flex-col hover:border-indigo-500/30 transition-all"
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold rounded-full shadow-lg shadow-indigo-500/25">
                    Most Popular
                  </div>
                )}

                <div className="relative h-32 mb-6 rounded-xl overflow-hidden bg-white/5">
                  <Image
                    src={plan.image}
                    alt={`${plan.name} plan`}
                    fill
                    className="object-contain p-4"
                  />
                </div>

                <h3 className="text-xl font-semibold text-white">{plan.name}</h3>
                <p className="mt-1 text-sm text-white/50">{plan.description}</p>

                <div className="mt-4 text-4xl font-bold text-white">
                  ${Math.round(display)}
                  <span className="text-lg text-white/50">/mo</span>
                  {annual && (
                    <span className="ml-2 align-middle text-xs font-medium text-emerald-400">
                      billed yearly
                    </span>
                  )}
                </div>
                {annual && (
                  <div className="mt-2 text-xs font-medium text-emerald-400">
                    Save ${savings}/yr vs monthly
                  </div>
                )}

                <ul className="mt-6 flex-1 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-white/70">
                      <svg className="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {f}
                    </li>
                  ))}
                </ul>

                <Button
                  className="mt-6 w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25"
                  onClick={() => handleCheckout(plan)}
                  disabled={checkout.isPending}
                >
                  {checkout.isPending
                    ? "Processing..."
                    : annual
                      ? `Subscribe annually — ${formatCentsCents(plan.monthlyCents * multiplier)}/yr`
                      : `Subscribe to ${plan.name}`}
                </Button>
              </motion.div>
            );
          })}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <h2 className="text-lg font-semibold text-white mb-2">Usage Estimator</h2>
            <p className="text-sm text-white/50 mb-4">
              Estimate your usage-based invoice for voice runtime and compute hours.
            </p>
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <label className="block text-xs text-white/50 mb-1">Compute hours</label>
                <Input
                  type="number"
                  min={0}
                  placeholder="e.g. 25"
                  value={usageUnits ?? ""}
                  onChange={(e) =>
                    setUsageUnits(e.target.value ? parseFloat(e.target.value) : null)
                  }
                />
              </div>
              <Button variant="outline" className="shrink-0" onClick={() => setUsageUnits(null)}>
                Clear
              </Button>
            </div>
            {usage.data && (
              <div className="mt-4 rounded-xl bg-white/5 border border-white/[0.04] p-4">
                <div className="text-sm text-white/60">{usage.data.label}</div>
                <div className="text-2xl font-bold text-white">
                  {formatCentsCents(usage.data.total_cents)}
                </div>
                <div className="text-xs text-white/40">at 50c/compute-hour - billed at usage</div>
              </div>
            )}
          </Card>

          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <h2 className="text-lg font-semibold text-white mb-2">Payment Grace</h2>
            <p className="text-sm text-white/50 mb-4">
              What happens if a card payment fails? Nobody loses access instantly.
            </p>
            <div className="rounded-xl bg-white/5 border border-white/[0.04] p-4 text-sm text-white/70 space-y-2">
              <p>
                <span className="text-emerald-400 font-medium">7-day grace period</span> - service keeps
                running while we retry the card.
              </p>
              <p>
                <span className="text-white/90 font-medium">Dunning emails</span> are drafted
                automatically and queue behind your approval gate - no surprise auto-sends.
              </p>
              <p className="text-white/50">
                Annual plans are immune: they are prepaid for the year.
              </p>
            </div>
          </Card>

          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <h2 className="text-lg font-semibold text-white mb-2">Referral Program</h2>
            <p className="text-sm text-white/50 mb-4">
              Earn while your network grows the swarm.
            </p>
            <div className="rounded-xl bg-white/5 border border-white/[0.04] p-4 text-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-white/70">You earn</span>
                <span className="text-emerald-400 font-medium">20% of first monthly payment</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/70">Friend gets</span>
                <span className="text-white/90 font-medium">20% off first month</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/70">Attribution window</span>
                <span className="text-white/90 font-medium">30 days</span>
              </div>
              <p className="text-white/50 pt-2 border-t border-white/10">
                Every referred signup is tracked; rewards are credited after their first payment.
              </p>
            </div>
          </Card>
        </div>

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <h2 className="text-lg font-semibold text-white mb-2">Current Plan</h2>
          <p className="text-sm text-white/50 mb-4">
            You are currently on the Free tier. Upgrade to unlock premium features.
          </p>
          <div className="p-4 rounded-xl bg-white/5 border border-white/[0.04]">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-white">Free Trial</div>
                <div className="text-xs text-white/50">Active - explore all features</div>
              </div>
              <div className="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-medium rounded">
                Active
              </div>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}