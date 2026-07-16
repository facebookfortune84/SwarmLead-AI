"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

import { User } from "@/types/user";

export function useCurrentUser() {
  return useQuery<User>({
    queryKey: [
      "current-user",
    ],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/users/me"
        );

      return response.data;
    },

    staleTime:
      1000 * 60 * 5,

    retry: 1,

    refetchOnWindowFocus:
      false,
  });
}