"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateLeadTicket } from "@/hooks/use-create-ticket";

interface TicketCreateDialogProps {
  leadId: string;
  leadEmail: string;
  onSuccess?: () => void;
}

export function TicketCreateDialog({ leadId, leadEmail, onSuccess }: TicketCreateDialogProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [department, setDepartment] = useState("sales");
  const [instruction, setInstruction] = useState("");
  const createTicket = useCreateLeadTicket();

  async function handleCreate() {
    if (!title.trim()) return;
    await createTicket.mutateAsync({ leadId, title, department, instruction });
    setTitle("");
    setInstruction("");
    setOpen(false);
    onSuccess?.();
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger className="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:opacity-90">
        Create Ticket
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Ticket for {leadEmail}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <Input placeholder="Ticket Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white"
          >
            <option value="sales">Sales</option>
            <option value="support">Support</option>
            <option value="engineering">Engineering</option>
            <option value="billing">Billing</option>
          </select>
          <textarea
            placeholder="Instructions / Description"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white resize-none h-24"
          />
          <Button className="w-full" onClick={handleCreate} disabled={createTicket.isPending || !title.trim()}>
            {createTicket.isPending ? "Creating..." : "Create Ticket"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}