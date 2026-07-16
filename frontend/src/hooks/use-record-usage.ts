"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  UsageRecord,
} from "@/types/usage";

export function useRecordUsage() {
  return useMutation({
    mutationFn: async (
      payload: UsageRecord
    ) => {
      const response =
        await api.post(
          "/api/usage/record",
          payload
        );

      return response.data;
    },
  });
}