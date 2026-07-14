"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/auth/me"
        );

      return response.data;
    },

    retry: false,
  });
}