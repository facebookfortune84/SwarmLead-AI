"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useMarkNotificationRead() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      notificationId: string
    ) => {
      const response =
        await api.post(
          `/api/notifications/read/${notificationId}`
        );

      return response.data;
    },

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          "notifications",
        ],
      });
    },
  });
}