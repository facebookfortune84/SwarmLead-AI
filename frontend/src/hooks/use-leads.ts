"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useLeads(
  limit = 100
) {
  return useQuery({
    queryKey: [
      "leads",
      limit,
    ],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/leads/",
          {
            params: {
              limit,
            },
          }
        );

      return (
        response.data
          ?.leads ?? []
      );
    },

    staleTime:
      30000,
  });
}