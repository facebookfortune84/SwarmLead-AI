"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useLeads() {
  return useQuery({
    queryKey: ["leads"],
    queryFn: async () => {
      const response =
        await api.get("/api/leads/");

      return response.data?.leads ?? [];
    },
  });
}