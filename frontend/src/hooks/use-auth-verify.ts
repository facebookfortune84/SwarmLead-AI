"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useAuthVerify() {
  return useQuery({
    queryKey: [
      "auth-verify",
    ],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/auth/verify"
        );

      return response.data;
    },

    retry: false,
  });
}