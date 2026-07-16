"use client";

import { Card } from "@/components/ui/card";

import {
  useWorkflowDetails,
} from "@/hooks/use-workflow-details";

import {
  WorkflowProgress,
} from "./workflow-progress";

import {
  WorkflowStepList,
} from "./workflow-step-list";

interface Props {
  workflowId: string;
}

export function WorkflowDetails({
  workflowId,
}: Props) {
  const {
    data,
    isLoading,
  } =
    useWorkflowDetails(
      workflowId
    );

  if (isLoading) {
    return (
      <Card className="p-6">
        Loading workflow...
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="p-6">
        Workflow not found.
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="grid gap-6 md:grid-cols-3">
          <div>
            <div className="text-sm text-muted-foreground">
              Status
            </div>

            <div className="font-semibold">
              {
                data.status
              }
            </div>
          </div>

          <div>
            <div className="text-sm text-muted-foreground">
              Current Step
            </div>

            <div className="font-semibold">
              {
                data.current_step
              }
            </div>
          </div>

          <div>
            <div className="text-sm text-muted-foreground">
              Total Steps
            </div>

            <div className="font-semibold">
              {
                data.total_steps
              }
            </div>
          </div>
        </div>

        <div className="mt-6">
          <WorkflowProgress
            currentStep={
              data.current_step ?? 0
            }
            totalSteps={
              data.total_steps ?? 0
            }
          />
        </div>

        {data.error_message && (
          <div className="mt-4 rounded border border-red-500 p-4 text-red-600">
            {
              data.error_message
            }
          </div>
        )}
      </Card>

      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold">
          Workflow Steps
        </h2>

        <WorkflowStepList
          steps={
            data.steps
          }
        />
      </Card>
    </div>
  );
}