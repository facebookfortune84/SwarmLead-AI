"use client";

import { Button } from "@/components/ui/button";

import {
  useStartWorkflow,
} from "@/hooks/use-start-workflow";

import {
  usePauseWorkflow,
} from "@/hooks/use-pause-workflow";

import {
  useResumeWorkflow,
} from "@/hooks/use-resume-workflow";

import {
  useCancelWorkflow,
} from "@/hooks/use-cancel-workflow";

interface Props {
  workflowId: string;

  status: string;
}

export function WorkflowControlPanel({
  workflowId,
  status,
}: Props) {
  const start =
    useStartWorkflow();

  const pause =
    usePauseWorkflow();

  const resume =
    useResumeWorkflow();

  const cancel =
    useCancelWorkflow();

  return (
    <div className="flex flex-wrap gap-2">
      {status ===
        "pending" && (
        <Button
          onClick={() =>
            start.mutate(
              workflowId
            )
          }
        >
          Start
        </Button>
      )}

      {status ===
        "running" && (
        <Button
          variant="outline"
          onClick={() =>
            pause.mutate(
              workflowId
            )
          }
        >
          Pause
        </Button>
      )}

      {status ===
        "paused" && (
        <Button
          onClick={() =>
            resume.mutate(
              workflowId
            )
          }
        >
          Resume
        </Button>
      )}

      {status !==
        "completed" &&
        status !==
          "failed" && (
          <Button
            variant="destructive"
            onClick={() =>
              cancel.mutate(
                workflowId
              )
            }
          >
            Cancel
          </Button>
        )}
    </div>
  );
}