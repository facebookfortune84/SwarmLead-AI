"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "sonner";

import { api } from "@/lib/api";

interface Payload {
  leadId: string;

  department?: string;

  title?: string;

  instruction?: string;
}

export function useCreateLeadTicket() {
  const queryClient = useQueryClient();

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
    onSuccess: (data) => {
      const ticketId =
        data?.ticket?.ticket_id;

      toast.success(
        ticketId
          ? `Ticket ${ticketId} created`
          : "Ticket created"
      );

      queryClient.invalidateQueries({
        queryKey: ["tickets"],
      });
    },
    onError: (error: any) => {
      const detail =
        error?.response?.data
          ?.detail ??
        error?.message ??
        "Could not create ticket";

      toast.error(
        typeof detail ===
          "string"
          ? detail
          : "Could not create ticket"
      );
    },
  });
}