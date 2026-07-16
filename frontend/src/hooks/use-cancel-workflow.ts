"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useCancelWorkflow() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      workflowId: string
    ) => {
      const response =
        await api.post(
          `/api/workflows/${workflowId}/cancel`
        );

      return response.data;
    },

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: [
          "workflows",
        ],
      });
    },
  });
}