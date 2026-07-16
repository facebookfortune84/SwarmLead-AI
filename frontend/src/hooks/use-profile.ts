"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

import { User } from "@/types/user";

export function useProfile() {
  return useQuery<User>({
    queryKey: [
      "profile",
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
  });
}