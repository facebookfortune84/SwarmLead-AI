"use client";

import { Workflow } from "@/types/workflow";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import {
  useWorkflowActions,
} from "@/hooks/use-workflow-actions";

import { WorkflowStatusBadge } from "./workflow-status-badge";

interface Props {
  workflow: Workflow;
}

export function WorkflowCard({
  workflow,
}: Props) {
  const actions =
    useWorkflowActions();

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold">
            {workflow.name}
          </h3>

          <div className="mt-2">
            <WorkflowStatusBadge
              status={
                workflow.status
              }
            />
          </div>

          <div className="mt-3 text-sm text-muted-foreground">
            Step{" "}
            {workflow.current_step ??
              0}
            {" / "}
            {workflow.total_steps ??
              0}
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={() =>
              actions.start.mutate(
                workflow.id
              )
            }
          >
            Start
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={() =>
              actions.pause.mutate(
                workflow.id
              )
            }
          >
            Pause
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={() =>
              actions.resume.mutate(
                workflow.id
              )
            }
          >
            Resume
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={() =>
              actions.cancel.mutate(
                workflow.id
              )
            }
          >
            Cancel
          </Button>
        </div>
      </div>

      {workflow.error_message && (
        <div className="mt-4 rounded-md border border-red-500 p-3 text-sm text-red-500">
          {workflow.error_message}
        </div>
      )}
    </Card>
  );
}