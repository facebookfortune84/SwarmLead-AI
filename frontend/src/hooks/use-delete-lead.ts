"use client";

import { useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useDeleteLead() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      leadId: string
    ) => {
      const response =
        await api.delete(
          `/api/leads/${leadId}`
        );

      return response.data;
    },

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: ["leads"],
      });
    },
  });
}