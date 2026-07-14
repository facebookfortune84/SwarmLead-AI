"use client";

import { useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function useWorkflowActions() {
  const qc =
    useQueryClient();

  function invalidate() {
    qc.invalidateQueries({
      queryKey: ["workflows"],
    });
  }

  const start =
    useMutation({
      mutationFn: async (
        workflowId: string
      ) => {
        const response =
          await api.post(
            `/api/workflows/${workflowId}/start`
          );

        return response.data;
      },

      onSuccess: invalidate,
    });

  const pause =
    useMutation({
      mutationFn: async (
        workflowId: string
      ) => {
        const response =
          await api.post(
            `/api/workflows/${workflowId}/pause`
          );

        return response.data;
      },

      onSuccess: invalidate,
    });

  const resume =
    useMutation({
      mutationFn: async (
        workflowId: string
      ) => {
        const response =
          await api.post(
            `/api/workflows/${workflowId}/resume`
          );

        return response.data;
      },

      onSuccess: invalidate,
    });

  const cancel =
    useMutation({
      mutationFn: async (
        workflowId: string
      ) => {
        const response =
          await api.post(
            `/api/workflows/${workflowId}/cancel`
          );

        return response.data;
      },

      onSuccess: invalidate,
    });

  return {
    start,
    pause,
    resume,
    cancel,
  };
}