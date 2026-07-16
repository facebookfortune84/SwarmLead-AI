"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  OutreachPayload,
} from "@/types/outreach";

export function useSendOutreach() {
  return useMutation({
    mutationFn: async (
      payload: OutreachPayload
    ) => {
      const response =
        await api.post(
          "/api/outreach/",
          payload
        );

      return response.data;
    },
  });
}