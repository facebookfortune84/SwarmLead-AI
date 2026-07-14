"use client";

import { useState } from "react";

import { Lead } from "@/types/lead";

import { Button } from "@/components/ui/button";

import { LeadEditDialog } from "./lead-edit-dialog";
import { LeadStatusMenu } from "./lead-status-menu";

import { WorkflowLauncher } from "@/components/workflows/workflow-launcher";

import { useDeleteLead } from "@/hooks/use-delete-lead";
import { useUpdateLead } from "@/hooks/use-update-lead";

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

  const updateLead =
    useUpdateLead();

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

  async function updateStatus(
    status: string
  ) {
    await updateLead.mutateAsync({
      id: lead.id,

      payload: {
        status,
      },
    });
  }

  return (
    <>
      <div className="flex flex-wrap gap-2">
        <LeadStatusMenu
          value={lead.status}
          onChange={updateStatus}
        />

        <WorkflowLauncher
          leadId={lead.id}
        />

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