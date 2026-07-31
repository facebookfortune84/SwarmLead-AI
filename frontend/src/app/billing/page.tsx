"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useCreateCheckoutSession } from "@/hooks/use-create-checkout-session";

interface Plan {
  name: string;
  price: string;
  amountCents: number;
  image: string;
  description: string;
  features: string[];
  popular?: boolean;
}

const PLANS: Plan[] = [
  {
    name: "Starter",
    price: "$29",
    amountCents: 2900,
    image: "/stripe_image_genesis_starter.png",
    description: "For small teams getting started with lead generation.",
    features: ["CRM & Lead Management", "Workflow Engine", "Single Tenant", "Basic Outreach", "Email Support"],
  },
  {
    name: "Growth",
    price: "$99",
    amountCents: 9900,
    image: "/stripe_image_genesis_growth.png",
    description: "Production-ready outreach and workflow automation.",
    features: ["Everything in Starter", "Advanced Workflows", "Multi-Tenant", "Campaign Outreach", "Reporting & Analytics", "Priority Support"],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "$299",
    amountCents: 29900,
    image: "/stripe_image_genesis_enterprise.png",
    description: "Large scale automation with AI agent runtime support.",
    features: ["Everything in Growth", "Unlimited Tenants", "Voice AI Runtime", "Custom Agent Development", "Dedicated Account Manager", "99.99% Uptime SLA"],
  },
];

export default function BillingPage() {
  const checkout = useCreateCheckoutSession();

  const handleCheckout = async (plan: Plan) => {
    try {
      const session = await checkout.mutateAsync({
        product_name: plan.name,
        amount_cents: plan.amountCents,
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
          <p className="text-white/50 mt-1">Choose the plan that fits your business. Upgrade or cancel anytime.</p>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-3">
          {PLANS.map((plan, i) => (
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
                {plan.price}
                <span className="text-lg text-white/50">/mo</span>
              </div>

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
                {checkout.isPending ? "Processing..." : `Subscribe to ${plan.name}`}
              </Button>
            </motion.div>
          ))}
        </div>

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <h2 className="text-lg font-semibold text-white mb-2">Current Plan</h2>
          <p className="text-sm text-white/50 mb-4">You are currently on the Free tier. Upgrade to unlock premium features.</p>
          <div className="p-4 rounded-xl bg-white/5 border border-white/[0.04]">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-white">Free Trial</div>
                <div className="text-xs text-white/50">Active — explore all features</div>
              </div>
              <div className="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-medium rounded">Active</div>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}