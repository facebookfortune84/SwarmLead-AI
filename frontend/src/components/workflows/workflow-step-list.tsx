"use client";

import {
  WorkflowStep,
} from "@/types/workflow";

interface Props {
  steps: WorkflowStep[];
}

export function WorkflowStepList({
  steps,
}: Props) {
  return (
    <div className="space-y-3">
      {steps.map(
        (step) => (
          <div
            key={step.id}
            className="rounded-lg border p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">
                  {
                    step.step_name
                  }
                </div>

                <div className="text-sm text-muted-foreground">
                  {
                    step.step_type
                  }
                </div>
              </div>

              <div className="rounded border px-3 py-1 text-xs">
                {
                  step.status
                }
              </div>
            </div>

            {step.error_message && (
              <div className="mt-3 rounded border border-red-500 p-3 text-sm text-red-600">
                {
                  step.error_message
                }
              </div>
            )}

            <div className="mt-2 text-xs text-muted-foreground">
              Retries:
              {" "}
              {
                step.retry_count
              }
            </div>
          </div>
        )
      )}
    </div>
  );
}