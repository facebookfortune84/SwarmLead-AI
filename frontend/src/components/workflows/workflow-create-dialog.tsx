"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useCreateWorkflow } from "@/hooks/use-create-workflow";

export function WorkflowCreateDialog() {
  const [name, setName] =
    useState("");

  const createWorkflow =
    useCreateWorkflow();

  async function save() {
    await createWorkflow.mutateAsync({
      name,
      steps: [
        {
          step_name:
            "Qualification",
          step_type:
            "notification",
        },
      ],
    });

    setName("");
  }

  return (
    <div className="rounded-lg border p-4">
      <div className="mb-3 font-medium">
        Create Workflow
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="Workflow Name"
          value={name}
          onChange={(e) =>
            setName(
              e.target.value
            )
          }
        />

        <Button onClick={save}>
          Create
        </Button>
      </div>
    </div>
  );
}