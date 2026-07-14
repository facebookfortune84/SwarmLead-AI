"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Lead } from "@/types/lead";

export function useLeads() {
  return useQuery<Lead[]>({
    queryKey: ["leads"],
    queryFn: async () => {
      const response = await api.get("/api/leads/");

      return response.data.leads;
    },
    staleTime: 30_000,
  });
}
