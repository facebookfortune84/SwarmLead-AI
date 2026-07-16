"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useMarkAllRead() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const response =
        await api.post(
          "/api/notifications/read-all"
        );

      return response.data;
    },

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: [
          "notifications",
        ],
      });
    },
  });
}