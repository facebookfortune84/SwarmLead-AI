"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TicketCreateDialog } from "./ticket-create-dialog";

interface Ticket {
  id: string;
  lead_id: string;
  title: string;
  department: string;
  status: string;
  created_at: string;
}

interface TicketListProps {
  tickets: Ticket[];
  onCreateTicket: (leadId: string, leadEmail: string) => void;
}

export function TicketList({ tickets, onCreateTicket }: TicketListProps) {
  if (tickets.length === 0) {
    return (
      <div className="rounded-lg border border-white/[0.06] p-12 text-center bg-white/[0.02]">
        <div className="text-lg font-semibold text-white">No Tickets</div>
        <div className="mt-2 text-sm text-white/50">Create a ticket to track support requests, escalations, and follow-ups.</div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tickets.map((ticket) => (
        <div
          key={ticket.id}
          className="flex items-center justify-between p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-indigo-500/20 transition-all"
        >
          <div>
            <div className="text-sm font-medium text-white">{ticket.title}</div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300">{ticket.department}</span>
              <span className="text-xs text-white/40">{ticket.status}</span>
            </div>
          </div>
          <div className="text-xs text-white/30">{new Date(ticket.created_at).toLocaleDateString()}</div>
        </div>
      ))}
    </div>
  );
}