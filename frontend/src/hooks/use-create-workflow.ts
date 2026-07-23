"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";

export interface WorkflowStepPayload {
  step_name: string;
  step_type: string;
  input?: Record<string, unknown>;
}

export interface CreateWorkflowPayload {
  name: string;
  company_id: string;
  steps: WorkflowStepPayload[];
}

export function useCreateWorkflow() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async (
      payload: CreateWorkflowPayload,
    ) => {
      const response =
        await api.post(
          "/api/workflows/",
          payload,
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