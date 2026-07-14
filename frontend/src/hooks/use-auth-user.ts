"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useAuthUser() {
  return useQuery({
    queryKey: ["auth-user"],

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