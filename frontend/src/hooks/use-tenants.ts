"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useTenants() {
  return useQuery({
    queryKey: ["tenants"],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/tenants"
        );

      return (
        response.data
          ?.tenants ?? []
      );
    },

    staleTime: 60_000,
  });
}