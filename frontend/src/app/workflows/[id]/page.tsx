"use client";

import { use } from "react";

import { AppShell } from "@/components/layout/app-shell";

import {
  WorkflowDetails,
} from "@/components/workflows/workflow-details";

export default function WorkflowPage({
  params,
}: {
  params: Promise<{
    id: string;
  }>;
}) {
  const { id } =
    use(params);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Workflow Operations
          </h1>

          <p className="text-muted-foreground">
            Live workflow monitoring and execution status.
          </p>
        </div>

        <WorkflowDetails
          workflowId={id}
        />
      </div>
    </AppShell>
  );
}