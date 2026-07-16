"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useTenantProvisionStatus(
  tenantId?: string
) {
  return useQuery({
    queryKey: [
      "tenant-provision-status",
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
      5000,

    staleTime: 0,
  });
}