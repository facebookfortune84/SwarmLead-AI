"use client";

import { Button } from "@/components/ui/button";

import {
  useCreateLeadTicket,
} from "@/hooks/use-create-ticket";

interface Props {
  leadId: string;
}

export function LeadTicketButton({
  leadId,
}: Props) {
  const createTicket =
    useCreateLeadTicket();

  return (
    <Button
      size="sm"
      onClick={() =>
        createTicket.mutate({
          leadId,
        })
      }
    >
      Create Ticket
    </Button>
  );
}