"use client";

import Link from "next/link";

import {
  useWorkflows,
} from "@/hooks/use-workflows";

type Workflow = {
  id: string;
  name: string;
  status?: string;
};

export function WorkflowHistoryList() {
  const {
    data = [],
    isLoading,
  } = useWorkflows();

  const workflows: Workflow[] = data as Workflow[];

  if (isLoading) {
    return (
      <div>
        Loading...
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {workflows.map((workflow) => (
        <Link key={workflow.id} href={`/workflows/${workflow.id}`} className="block rounded-md p-4 border">
          <div className="font-medium">{workflow.name}</div>
          <div className="text-sm text-muted-foreground">{workflow.status}</div>
        </Link>
      ))}
    </div>
  );
}