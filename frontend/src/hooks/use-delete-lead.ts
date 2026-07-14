"use client";

import { useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useDeleteLead() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      id: string
    ) => {
      const response =
        await api.delete(
          `/api/leads/${id}`
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