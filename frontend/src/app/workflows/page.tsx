"use client";

import { AppShell } from "@/components/layout/app-shell";

import { Card } from "@/components/ui/card";

import {
  WorkflowCreateForm,
} from "@/components/workflows/workflow-create-form";

import {
  WorkflowHistoryList,
} from "@/components/workflows/workflow-history-list";

import {
  WorkflowOverviewCard,
} from "@/components/workflows/workflow-overview-card";

export default function WorkflowsPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Workflow Center
          </h1>

          <p className="text-muted-foreground">
            Automation runtime,
            orchestration,
            execution,
            and workflow operations.
          </p>
        </div>

        <WorkflowOverviewCard />

        <Card className="p-6">
          <h2 className="mb-4 font-semibold">
            Create Workflow
          </h2>

          <WorkflowCreateForm />
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 font-semibold">
            Workflow History
          </h2>

          <WorkflowHistoryList />
        </Card>
      </div>
    </AppShell>
  );
}