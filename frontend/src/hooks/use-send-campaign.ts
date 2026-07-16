"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  CampaignPayload,
} from "@/types/outreach";

export function useSendCampaign() {
  return useMutation({
    mutationFn: async (
      payload: CampaignPayload
    ) => {
      const response =
        await api.post(
          "/api/outreach/campaign",
          payload
        );

      return response.data;
    },
  });
}