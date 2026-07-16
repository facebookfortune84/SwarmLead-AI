"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

interface Payload {
  name: string;

  slug?: string;
}

export function useRegisterTenant() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      payload: Payload
    ) => {
      const response =
        await api.post(
          "/api/tenants/register",
          payload
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