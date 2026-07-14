"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useStartWorkflow() {
  return useMutation({
    mutationFn: async (
      workflowId: string
    ) => {
      const response =
        await api.post(
          `/api/workflows/${workflowId}/start`
        );

      return response.data;
    },
  });
}

export function usePauseWorkflow() {
  return useMutation({
    mutationFn: async (
      workflowId: string
    ) => {
      const response =
        await api.post(
          `/api/workflows/${workflowId}/pause`
        );

      return response.data;
    },
  });
}

export function useResumeWorkflow() {
  return useMutation({
    mutationFn: async (
      workflowId: string
    ) => {
      const response =
        await api.post(
          `/api/workflows/${workflowId}/resume`
        );

      return response.data;
    },
  });
}