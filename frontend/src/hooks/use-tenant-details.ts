"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useTenantDetails(
  tenantId?: string
) {
  return useQuery({
    queryKey: [
      "tenant",
      tenantId,
    ],

    enabled:
      !!tenantId,

    queryFn: async () => {
      const response =
        await api.get(
          `/api/tenants/${tenantId}`
        );

      return response.data;
    },
  });
}