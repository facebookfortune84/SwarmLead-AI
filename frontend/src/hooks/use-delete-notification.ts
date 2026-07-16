"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useDeleteNotification() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      notificationId: string
    ) => {
      const response =
        await api.delete(
          `/api/notifications/${notificationId}`
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