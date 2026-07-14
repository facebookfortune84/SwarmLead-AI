"use client";

import { useState } from "react";

import { Lead } from "@/types/lead";

import { Button } from "@/components/ui/button";

import { LeadEditDialog } from "./lead-edit-dialog";

import { useDeleteLead } from "@/hooks/use-delete-lead";

interface Props {
  lead: Lead;
}

export function LeadActions({
  lead,
}: Props) {
  const [editing, setEditing] =
    useState(false);

  const deleteLead =
    useDeleteLead();

  async function handleDelete() {
    const confirmed =
      window.confirm(
        `Delete lead ${lead.email}?`
      );

    if (!confirmed) {
      return;
    }

    await deleteLead.mutateAsync(
      lead.id
    );
  }

  return (
    <>
      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={() =>
            setEditing(true)
          }
        >
          Edit
        </Button>

        <Button
          variant="outline"
          onClick={handleDelete}
        >
          Delete
        </Button>
      </div>

      <LeadEditDialog
        lead={lead}
        open={editing}
        onOpenChange={
          setEditing
        }
      />
    </>
  );
}