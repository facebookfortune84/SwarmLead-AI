"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

type ApprovalItem = {
  id: string;
  kind: "outreach_send" | "quote_send";
  status: string;
  created_at: string;
  payload: {
    to_email: string;
    lead_name?: string;
    subject: string;
    body: string;
    tier?: string;
    checkout_url?: string;
  };
};

export type GrowthStatus = {
  enabled: boolean;
  cycle_hours: number;
  cycle_count: number;
  last_run: string | null;
  next_run: number | null;
  funnel: Record<string, unknown>;
  learned_keyword_boosts: Record<string, number>;
  discovery?: {
    findings: number;
    recent: { email: string; company?: string; vertical?: string; intent_score?: number }[];
  };
  artifacts: { seo_pages: number; content_drafts: number };
  approval_queue: {
    total: number;
    pending: number;
    pending_outreach: number;
    pending_quotes: number;
    pending_dunning?: number;
  };
};

export function useGrowthStatus() {
  return useQuery({
    queryKey: ["growth-status"],
    queryFn: async () => {
      const { data } = await api.get<GrowthStatus>("/api/growth/status");
      return data;
    },
    refetchInterval: 30000,
  });
}

export function useGrowthQueue() {
  return useQuery({
    queryKey: ["growth-queue"],
    queryFn: async () => {
      const { data } = await api.get<{ items: ApprovalItem[] }>("/api/growth/queue");
      return data.items;
    },
    refetchInterval: 30000,
  });
}

export function useApproveAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/api/growth/approve/${id}`);
      return data;
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["growth-status"] });
      qc.invalidateQueries({ queryKey: ["growth-queue"] });
    },
  });
}

export function useRejectAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/api/growth/reject/${id}`);
      return data;
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["growth-status"] });
      qc.invalidateQueries({ queryKey: ["growth-queue"] });
    },
  });
}

export function useRunNow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post("/api/growth/run-now");
      return data;
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["growth-status"] });
      qc.invalidateQueries({ queryKey: ["growth-queue"] });
    },
  });
}

export function useToggleGrowth() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (enabled: boolean) => {
      const { data } = await api.post("/api/growth/toggle", { enabled });
      return data;
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["growth-status"] });
    },
  });
}

export function usePurgeAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/api/growth/purge/${id}`);
      return data;
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["growth-status"] });
      qc.invalidateQueries({ queryKey: ["growth-queue"] });
    },
  });
}

export function usePurgeAllPending() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post("/api/growth/purge-all");
      return data;
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["growth-status"] });
      qc.invalidateQueries({ queryKey: ["growth-queue"] });
    },
  });
}
