"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

interface Payload {
  full_name?: string;

  email?: string;
}

export function useUpdateProfile() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      payload: Payload
    ) => {
      const response =
        await api.put(
          "/api/users/me",
          payload
        );

      return response.data;
    },

    onSuccess: () => {
      qc.invalidateQueries(
        {
          queryKey: [
            "profile",
          ],
        }
      );

      qc.invalidateQueries(
        {
          queryKey: [
            "current-user",
          ],
        }
      );
    },
  });
}