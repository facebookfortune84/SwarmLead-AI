"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface RevenueSummary {
  mrr_cents: number;
  arr_cents: number;
  annual_contract_cents: number;
  open_weighted_annual_cents: number;
  closed_won_count: number;
  quotes_approved: number;
  quotes_expected_mrr_cents: number;
  tier_mix: Record<
    string,
    {
      count: number;
      mrr_cents: number;
    }
  >;
  as_of: string;
}

export interface BillingTiers {
  annual_multiplier: number;
  tiers: Record<
    string,
    {
      name: string;
      monthly_cents: number;
      annual_cents: number;
      annual_savings_cents: number;
    }
  >;
}

export interface ChurnReport {
  risk: {
    at_risk_deals: Array<{
      deal_id: string;
      email: string;
      stage: string;
      days_inactive: number;
    }>;
    safe_deals: number;
    lookback_days: number;
    risk_rate: number;
  };
  retention_curve: Array<{
    month: number;
    retention_rate: number;
    churn_rate: number;
  }>;
  ltv: {
    ltv_cents: number;
    mrr_cents: number;
    churn_rate: number;
    avg_customer_lifetime_months: number;
  };
}

export function useRevenueSummary() {
  return useQuery({
    queryKey: ["revenue-summary"],
    queryFn: async () => {
      const { data } = await api.get<RevenueSummary>("/api/revenue/summary");
      return data;
    },
    refetchInterval: 60000,
  });
}

export function useBillingTiers() {
  return useQuery({
    queryKey: ["revenue-tiers"],
    queryFn: async () => {
      const { data } = await api.get<BillingTiers>("/api/revenue/tiers");
      return data;
    },
    staleTime: 60_000,
  });
}

export function useChurnReport() {
  return useQuery({
    queryKey: ["revenue-churn"],
    queryFn: async () => {
      const { data } = await api.get<ChurnReport>("/api/revenue/churn", {
        params: { months: 12 },
      });
      return data;
    },
    refetchInterval: 60000,
  });
}

export function useUsageInvoice(units: number, rateCents: number) {
  return useQuery({
    queryKey: ["usage-invoice", units, rateCents],
    queryFn: async () => {
      const { data } = await api.get<{
        label: string;
        total_cents: number;
        subtotal_usd: number;
      }>("/api/revenue/usage", {
        params: { units, rate_cents: rateCents },
      });
      return data;
    },
    enabled: units > 0,
  });
}