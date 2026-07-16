"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

import { Lead } from "@/types/lead";

export function useLeads(
  limit = 100
) {
  return useQuery<Lead[]>({
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
      ) as Lead[];
    },
  });
}