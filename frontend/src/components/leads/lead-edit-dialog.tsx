"use client";

import { useState } from "react";

import { Lead } from "@/types/lead";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useUpdateLead } from "@/hooks/use-update-lead";

interface Props {
  open: boolean;
  onOpenChange: (
    open: boolean
  ) => void;

  lead: Lead;
}

export function LeadEditDialog({
  open,
  onOpenChange,
  lead,
}: Props) {
  const updateLead =
    useUpdateLead();

  const [
    email,
    setEmail,
  ] = useState(
    lead.email
  );

  const [
    name,
    setName,
  ] = useState(
    lead.name ?? ""
  );

  const [
    company,
    setCompany,
  ] = useState(
    lead.company ?? ""
  );

  async function save() {
    await updateLead.mutateAsync({
      id: lead.id,

      payload: {
        email,
        name,
        company,
      },
    });

    onOpenChange(false);
  }

  return (
    <Dialog
      open={open}
      onOpenChange={
        onOpenChange
      }
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Edit Lead
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Input
            value={email}
            onChange={(e) =>
              setEmail(
                e.target.value
              )
            }
          />

          <Input
            value={name}
            onChange={(e) =>
              setName(
                e.target.value
              )
            }
          />

          <Input
            value={company}
            onChange={(e) =>
              setCompany(
                e.target.value
              )
            }
          />

          <Button
            className="w-full"
            onClick={save}
          >
            Save Changes
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}