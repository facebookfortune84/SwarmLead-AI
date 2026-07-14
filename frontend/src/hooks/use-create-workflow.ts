"use client";

import { useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

interface WorkflowStep {
  step_name: string;

  step_type: string;

  input?: Record<
    string,
    unknown
  >;
}

export function useCreateWorkflow() {
  const qc =
    useQueryClient();

  return useMutation({
    mutationFn: async ({
      name,
      steps,
      company_id,
    }: {
      name: string;

      steps: WorkflowStep[];

      company_id?: string;
    }) => {
      const response =
        await api.post(
          "/api/workflows",
          {
            name,
            steps,
            company_id,
          }
        );

      return response.data;
    },

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: ["workflows"],
      });
    },
  });
}