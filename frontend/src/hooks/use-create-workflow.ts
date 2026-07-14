"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useCreateWorkflow() {
  return useMutation({
    mutationFn: async ({
      name,
      steps,
    }: {
      name: string;
      steps: unknown[];
    }) => {
      const response =
        await api.post(
          "/api/workflows",
          {
            name,
            steps,
          }
        );

      return response.data;
    },
  });
}