"use client";

import { AppShell } from "@/components/layout/app-shell";

import {
  PricingCard,
} from "@/components/billing/pricing-card";

export default function BillingPage() {
  return (
    <AppShell>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold">
            Billing
          </h1>

          <p className="text-muted-foreground">
            Subscription
            management,
            platform access,
            workflow limits,
            outreach capacity,
            and future agent runtime licensing.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <PricingCard
            name="Starter"
            price="$29/mo"
            amountCents={2900}
            description="For small teams getting started with lead generation."
            features={[
              "CRM",
              "Lead Management",
              "Workflow Engine",
              "Single Tenant",
              "Basic Outreach",
            ]}
          />

          <PricingCard
            name="Professional"
            price="$99/mo"
            amountCents={9900}
            description="Production-ready outreach and workflow automation."
            features={[
              "Everything in Starter",
              "Advanced Workflows",
              "Tenants",
              "Notifications",
              "Campaign Outreach",
              "Reporting",
            ]}
          />

          <PricingCard
            name="Enterprise"
            price="$299/mo"
            amountCents={29900}
            description="Large scale automation, orchestration, and future AI agent runtime support."
            features={[
              "Everything in Professional",
              "Multi-Tenant",
              "Advanced Analytics",
              "Voice Runtime",
              "Agent Runtime",
              "Priority Support",
            ]}
          />
        </div>
      </div>
    </AppShell>
  );
}