"use client";

import Link from "next/link";

import { Card } from "@/components/ui/card";

import {
  WorkflowStatusBadge,
} from "./workflow-status-badge";

interface WorkflowRuntime {
  id: string;

  name: string;

  status: string;
}

interface Props {
  workflow: WorkflowRuntime;
}

export function WorkflowRuntimeCard({
  workflow,
}: Props) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-medium">
            {workflow.name}
          </div>

          <div className="mt-2">
            <WorkflowStatusBadge
              status={workflow.status}
            />
          </div>
        </div>

        <Link
          href={`/workflows/${workflow.id}`}
          className="text-sm font-medium text-primary-600 hover:underline"
        >
          View
        </Link>
      </div>
    </Card>
  );
}