"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export interface Tenant {
  id: string;

  name: string;

  slug?: string;

  status?: string;

  created_at?: string;
}

export function useTenantList() {
  return useQuery({
    queryKey: [
      "tenants",
    ],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/tenants"
        );

      return (
        response.data
          ?.tenants ?? []
      ) as Tenant[];
    },

    staleTime:
      30000,
  });
}