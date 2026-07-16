"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useTenantStatus(
  tenantId?: string
) {
  return useQuery({
    queryKey: [
      "tenant-status",
      tenantId,
    ],

    enabled:
      !!tenantId,

    queryFn: async () => {
      const response =
        await api.get(
          `/api/tenants/${tenantId}/status`
        );

      return response.data;
    },

    refetchInterval:
      10000,
  });
}