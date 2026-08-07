"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface ConciergeTurn {
  session_id: string;
  step: string;
  done: boolean;
  prompt: string;
  brief: string;
  company: string;
  domain: string;
  domains: Array<{ domain: string; available: boolean }>;
  candidates: Array<{ name: string; available: boolean }>;
  launch_signal: boolean;
  history: Array<{ role: string; content: string }>;
}

export type ConciergeStatus = {
  sessions: number;
  steps: string[];
  taken_names: number;
  tlds: string[];
};

export interface LaunchConcierge {
  start: (payload: { founder_name?: string; opening_line?: string }) => Promise<ConciergeTurn>;
  turn: (session_id: string, text: string) => Promise<ConciergeTurn>;
  get: (session_id: string) => Promise<unknown>;
  end: (session_id: string) => Promise<unknown>;
  status: () => Promise<ConciergeStatus>;
}

export function useLaunchConcierge(): LaunchConcierge {
  return {
    start: (payload) =>
      api.post("/api/launch/concierge/start", payload).then((r) => r.data),
    turn: (session_id, text) =>
      api
        .post("/api/launch/concierge/message", { session_id, text })
        .then((r) => r.data),
    get: (session_id) =>
      api.get(`/api/launch/concierge/${session_id}`).then((r) => r.data),
    end: (session_id) =>
      api.post(`/api/launch/concierge/${session_id}/end`).then((r) => r.data),
    status: () => api.get("/api/launch/concierge/status").then((r) => r.data),
  };
}

export function useConciergeStatus() {
  return useQuery({
    queryKey: ["concierge-status"],
    queryFn: () => api.get("/api/launch/concierge/status").then((r) => r.data),
    refetchInterval: 30_000,
  });
}

export function useConciergeStart() {
  return useMutation({
    mutationFn: (payload: { founder_name?: string; opening_line?: string }) =>
      api.post("/api/launch/concierge/start", payload).then((r) => r.data),
  });
}

export function useConciergeTurn() {
  return useMutation({
    mutationFn: ({ session_id, text }: { session_id: string; text: string }) =>
      api
        .post("/api/launch/concierge/message", { session_id, text })
        .then((r) => r.data),
  });
}

// ---- outreach maximization + nurture (acquisition ballistics) -------------

export interface Lever {
  key: string;
  label: string;
  category: string;
  action: string;
  relevance: number;
}

export interface MaximizeResult {
  lead: string;
  score: number;
  band: string;
  levers: Lever[];
  suggested_subject: string;
  suggested_hook: string;
  ready: boolean;
}

export function useMaximize(lead: Record<string, unknown> | null) {
  return useQuery({
    queryKey: ["maximize", lead],
    queryFn: () =>
      api.post("/api/launch/maximize", lead ?? {}).then((r) => r.data),
    enabled: !!lead,
  });
}

export function useMaximizeLevers() {
  return useQuery({
    queryKey: ["maximize-levers"],
    queryFn: () => api.get("/api/launch/maximize/levers").then((r) => r.data),
  });
}

export function useNurturePlan(email: string | null) {
  return useQuery({
    queryKey: ["nurture", email],
    queryFn: () =>
      api
        .post("/api/launch/nurture/plan", { email: email ?? "" })
        .then((r) => r.data),
    enabled: !!email,
  });
}

export function useNurtureClassify() {
  return useMutation({
    mutationFn: (reply: string) =>
      api
        .post("/api/launch/nurture/classify", { reply })
        .then((r) => r.data),
  });
}