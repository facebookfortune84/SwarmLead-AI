"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useDeleteUser() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      userId: string
    ) => {
      const response =
        await api.delete(
          `/api/users/${userId}`
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