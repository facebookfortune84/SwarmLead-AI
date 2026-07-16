"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useProvisionTenant() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      tenantId: string
    ) => {
      const response =
        await api.post(
          `/api/tenants/${tenantId}/provision`,
          {
            use_vm:
              false,
          }
        );

      return response.data;
    },

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: [
          "tenants",
        ],
      });
    },
  });
}