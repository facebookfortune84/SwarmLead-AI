"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface PipelineStage {
  stage: string;
  count: number;
  weighted_value_cents: number;
  probability: number;
}

export interface PipelineSnapshot {
  stages: PipelineStage[];
  total_deals: number;
  open_deals: number;
  weighted_pipeline_cents: number;
  generated_at: string;
}

export interface SalesForecast {
  open_weighted_mrr_cents: number;
  open_weighted_annual_cents: number;
  closed_won_mrr_cents: number;
  closed_won_annual_cents: number;
  closed_won_count: number;
  annual_contract_cents: number;
  as_of: string;
}

export interface Deal {
  id: string;
  lead_id: string;
  email: string;
  company: string | null;
  stage: string;
  amount_cents: number;
  probability: number;
  intent_score: number | null;
  notes: string | null;
  owner_agent: string | null;
  active: boolean;
  created_at: string;
  weighted_value_cents: number;
}

export function usePipelineSnapshot() {
  return useQuery({
    queryKey: ["sales-pipeline"],
    queryFn: async () => {
      const { data } = await api.get<PipelineSnapshot>("/api/sales/pipeline");
      return data;
    },
    refetchInterval: 30000,
  });
}

export function useSalesForecast() {
  return useQuery({
    queryKey: ["sales-forecast"],
    queryFn: async () => {
      const { data } = await api.get<SalesForecast>("/api/sales/forecast");
      return data;
    },
    refetchInterval: 30000,
  });
}

export function useSalesDeals(stage?: string) {
  return useQuery({
    queryKey: ["sales-deals", stage ?? "all"],
    queryFn: async () => {
      const { data } = await api.get<{ deals: Deal[] }>("/api/sales/deals", {
        params: stage ? { stage } : {},
      });
      return data.deals;
    },
    refetchInterval: 30000,
  });
}
