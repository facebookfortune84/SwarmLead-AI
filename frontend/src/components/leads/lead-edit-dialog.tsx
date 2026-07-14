"use client";

import {
  useEffect,
  useState,
} from "react";

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

  lead: Lead | null;
}

export function LeadEditDialog({
  open,
  onOpenChange,
  lead,
}: Props) {
  const updateLead =
    useUpdateLead();

  const [email, setEmail] =
    useState("");

  const [name, setName] =
    useState("");

  const [company, setCompany] =
    useState("");

  const [status, setStatus] =
    useState("NEW");

  const [owner, setOwner] =
    useState("");

  const [notes, setNotes] =
    useState("");

  useEffect(() => {
    if (!lead) return;
    // Defer state updates to avoid synchronous setState within effect
    const t = setTimeout(() => {
      setEmail(lead.email ?? "");
      setName(lead.name ?? "");
      setCompany(lead.company ?? "");
      setStatus(lead.status ?? "NEW");
      setOwner(lead.owner ?? "");
      setNotes(lead.notes ?? "");
    }, 0);

    return () => clearTimeout(t);
  }, [lead]);

  if (!lead) return null;

  async function handleSave() {
    if (!lead) return;

    await updateLead.mutateAsync({
      id: lead.id,

      payload: {
        email,
        name,
        company,
        status,
        owner,
        notes,
      },
    });

    onOpenChange(false);
  }

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
    >
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>
            Edit Lead
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Input
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(
                e.target.value
              )
            }
          />

          <Input
            placeholder="Name"
            value={name}
            onChange={(e) =>
              setName(
                e.target.value
              )
            }
          />

          <Input
            placeholder="Company"
            value={company}
            onChange={(e) =>
              setCompany(
                e.target.value
              )
            }
          />

          <Input
            placeholder="Status"
            value={status}
            onChange={(e) =>
              setStatus(
                e.target.value
              )
            }
          />

          <Input
            placeholder="Owner"
            value={owner}
            onChange={(e) =>
              setOwner(
                e.target.value
              )
            }
          />

          <Input
            placeholder="Notes"
            value={notes}
            onChange={(e) =>
              setNotes(
                e.target.value
              )
            }
          />

          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() =>
                onOpenChange(false)
              }
            >
              Cancel
            </Button>

            <Button
              className="flex-1"
              onClick={handleSave}
              disabled={
                updateLead.isPending
              }
            >
              {updateLead.isPending
                ? "Saving..."
                : "Save Changes"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}