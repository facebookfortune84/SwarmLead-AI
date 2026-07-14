"use client";

import { AgentRegistry } from "@/components/agents/agent-registry";

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Agent Center
        </h1>

        <p className="text-muted-foreground">
          Agent orchestration,
          automation,
          outreach,
          qualification,
          and future voice execution.
        </p>
      </div>

      <AgentRegistry />
    </div>
  );
}