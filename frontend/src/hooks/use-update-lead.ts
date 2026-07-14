"use client";

import { useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useUpdateLead() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string;
      payload: Record<
        string,
        unknown
      >;
    }) => {
      const response =
        await api.put(
          `/api/leads/${id}`,
          payload
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