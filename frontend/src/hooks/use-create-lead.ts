"use client";

import { useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useCreateLead() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: async (payload: {
      email: string;
      name?: string;
      company?: string;
    }) => {
      const response =
        await api.post(
          "/api/leads/",
          payload
        );

      return response.data;
    },

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["leads"],
      });
    },
  });
}