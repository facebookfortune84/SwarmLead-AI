"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useCreateWorkflow() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async (
      payload: {
        name: string;

        steps: {
          step_name: string;
          step_type: string;
          input?: Record<
            string,
            unknown
          >;
        }[];
      }
    ) => {
      const response =
        await api.post(
          "/api/workflows/",
          payload
        );

      return response.data;
    },

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: [
          "workflows",
        ],
      });
    },
  });
}