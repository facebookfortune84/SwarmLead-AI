"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useWorkflows() {
  return useQuery({
    queryKey: ["workflows"],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/workflows"
        );

      return (
        response.data
          ?.workflows ?? []
      );
    },

    retry: false,
  });
}