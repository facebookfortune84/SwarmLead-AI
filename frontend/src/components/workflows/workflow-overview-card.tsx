"use client";

import { Card } from "@/components/ui/card";

import {
  useWorkflows,
} from "@/hooks/use-workflows";

interface WorkflowRuntime {
  id: string;
  name: string;
  status: string;
}

export function WorkflowOverviewCard() {
  const {
    data = [],
  } = useWorkflows();

  const workflows =
    data as WorkflowRuntime[];

  const running =
    workflows.filter(
      (workflow) =>
        workflow.status ===
        "running"
    ).length;

  const completed =
    workflows.filter(
      (workflow) =>
        workflow.status ===
        "completed"
    ).length;

  const failed =
    workflows.filter(
      (workflow) =>
        workflow.status ===
        "failed"
    ).length;

  return (
    <Card className="p-6">
      <h2 className="font-semibold">
        Workflow Metrics
      </h2>

      <div className="mt-4 space-y-3">
        <div>
          Running: {running}
        </div>

        <div>
          Completed: {completed}
        </div>

        <div>
          Failed: {failed}
        </div>
      </div>
    </Card>
  );
}