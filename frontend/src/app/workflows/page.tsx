"use client";

import { Card } from "@/components/ui/card";

import { useWorkflows } from "@/hooks/use-workflows";

import { WorkflowCard } from "@/components/workflows/workflow-card";
import { WorkflowCreateDialog } from "@/components/workflows/workflow-create-dialog";

import { Workflow } from "@/types/workflow";

export default function WorkflowsPage() {
  const {
    data = [],
    isLoading,
    error,
  } = useWorkflows();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Workflow Center
          </h1>

          <p className="text-muted-foreground">
            Automation, orchestration,
            outreach execution,
            qualification pipelines,
            and future voice routing.
          </p>
        </div>

        <WorkflowCreateDialog />
      </div>

      {error ? (
        <Card className="p-6">
          <div className="font-medium">
            Authentication Required
          </div>

          <div className="mt-2 text-sm text-muted-foreground">
            Login is required before workflows
            can be viewed or executed.
          </div>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="p-6">
          Loading workflows...
        </Card>
      ) : data.length === 0 ? (
        <Card className="p-6">
          <div className="font-medium">
            No workflows found
          </div>

          <div className="mt-2 text-sm text-muted-foreground">
            Create a workflow to begin
            automation.
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {data.map(
            (workflow: Workflow) => (
              <WorkflowCard
                key={workflow.id}
                workflow={workflow}
              />
            )
          )}
        </div>
      )}
    </div>
  );
}