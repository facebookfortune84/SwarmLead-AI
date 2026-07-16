"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  WorkflowDetail,
} from "@/types/workflow";

export function useWorkflowDetails(
  workflowId?: string
) {
  return useQuery<WorkflowDetail>({
    queryKey: [
      "workflow",
      workflowId,
    ],

    enabled:
      !!workflowId,

    queryFn: async () => {
      const response =
        await api.get(
          `/api/workflows/${workflowId}`
        );

      return response.data;
    },

    staleTime: 15000,

    refetchInterval: 5000,
  });
}