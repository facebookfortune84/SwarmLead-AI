"use client";

import {
  useWorkflows,
} from "@/hooks/use-workflows";

import {
  WorkflowRuntimeCard,
} from "./workflow-runtime-card";

interface WorkflowRuntime {
  id: string;
  name: string;
  status: string;
}

export function WorkflowRuntimeGrid() {
  const {
    data = [],
    isLoading,
  } = useWorkflows();

  if (isLoading) {
    return (
      <div>
        Loading...
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {(
        data as WorkflowRuntime[]
      ).map((workflow) => (
        <WorkflowRuntimeCard
          key={workflow.id}
          workflow={workflow}
        />
      ))}
    </div>
  );
}