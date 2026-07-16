"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useActivateUser() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      userId: string
    ) => {
      const response =
        await api.post(
          `/api/users/${userId}/activate`
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