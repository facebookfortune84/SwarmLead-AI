"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useLeadTimeline(
  leadId?: string
) {
  return useQuery({
    queryKey: [
      "lead-timeline",
      leadId,
    ],

    enabled:
      !!leadId,

    queryFn: async () => {
      const response =
        await api.get(
          `/api/leads/${leadId}/timeline`
        );

      return response.data;
    },
  });
}