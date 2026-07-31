"use client";

import { Workflow } from "@/types/workflow";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import {
  useWorkflowActions,
} from "@/hooks/use-workflow-actions";

import { WorkflowStatusBadge } from "./workflow-status-badge";

import { Play, Pause, PlayCircle, XCircle, Loader2, AlertCircle } from "lucide-react";

interface Props {
  workflow: Workflow;
}

export function WorkflowCard({
  workflow,
}: Props) {
  const actions =
    useWorkflowActions();

  const anyPending =
    actions.start.isPending ||
    actions.pause.isPending ||
    actions.resume.isPending ||
    actions.cancel.isPending;

  const mutationError =
    actions.start.error ??
    actions.pause.error ??
    actions.resume.error ??
    actions.cancel.error;

  return (
    <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-white">
            {workflow.name}
          </h3>

          <div className="mt-2">
            <WorkflowStatusBadge
              status={
                workflow.status
              }
            />
          </div>

          <div className="mt-3 text-sm text-white/50">
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
            disabled={anyPending || workflow.status === "running"}
          >
            {actions.start.isPending ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" />
            ) : (
              <Play className="w-3.5 h-3.5 mr-1" />
            )}
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
            disabled={anyPending || workflow.status !== "running"}
          >
            {actions.pause.isPending ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" />
            ) : (
              <Pause className="w-3.5 h-3.5 mr-1" />
            )}
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
            disabled={anyPending || workflow.status !== "paused"}
          >
            {actions.resume.isPending ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" />
            ) : (
              <PlayCircle className="w-3.5 h-3.5 mr-1" />
            )}
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
            disabled={anyPending || workflow.status === "completed" || workflow.status === "failed"}
          >
            {actions.cancel.isPending ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" />
            ) : (
              <XCircle className="w-3.5 h-3.5 mr-1" />
            )}
            Cancel
          </Button>
        </div>
      </div>

      {mutationError && (
        <div className="mt-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {mutationError instanceof Error ? mutationError.message : "Action failed"}
        </div>
      )}

      {workflow.error_message && (
        <div className="mt-4 rounded-md border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">
          {workflow.error_message}
        </div>
      )}
    </Card>
  );
}
