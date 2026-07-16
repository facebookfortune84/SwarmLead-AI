"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

import { User } from "@/types/user";

interface Options {
  skip?: number;
  limit?: number;
}

export function useUsers(
  options: Options = {}
) {
  const {
    skip = 0,
    limit = 100,
  } = options;

  return useQuery<User[]>({
    queryKey: [
      "users",
      skip,
      limit,
    ],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/users/",
          {
            params: {
              skip,
              limit,
            },
          }
        );

      return response.data;
    },

    staleTime: 30000,
  });
}