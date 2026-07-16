"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useSuspendUser() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      userId: string
    ) => {
      const response =
        await api.post(
          `/api/users/${userId}/suspend`
        );

      return response.data;
    },

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: [
          "users",
        ],
      });
    },
  });
}