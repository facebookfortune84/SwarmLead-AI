"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

interface UpdateUserPayload {
  userId: string;

  full_name?: string;

  email?: string;
}

export function useUpdateUser() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async ({
      userId,
      ...payload
    }: UpdateUserPayload) => {
      const response =
        await api.put(
          `/api/users/${userId}`,
          payload
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