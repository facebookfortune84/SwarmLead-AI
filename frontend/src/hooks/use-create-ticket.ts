"use client";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

interface Payload {
  leadId: string;

  department?: string;

  title?: string;

  instruction?: string;
}

export function useCreateLeadTicket() {
  return useMutation({
    mutationFn: async ({
      leadId,
      department = "sales",
      title = "Follow-up",
      instruction =
        "Contact lead",
    }: Payload) => {
      const response =
        await api.post(
          `/api/leads/${leadId}/ticket`,
          null,
          {
            params: {
              department,
              title,
              instruction,
            },
          }
        );

      return response.data;
    },
  });
}