"use client";

import { Card } from "@/components/ui/card";

export default function WorkflowsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Workflows
        </h1>

        <p className="text-muted-foreground">
          Automation, outreach, qualification,
          voice agents, and human escalation.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <h2 className="font-semibold">
            Lead Qualification
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            Automatically score and qualify
            incoming leads.
          </p>
        </Card>

        <Card className="p-6">
          <h2 className="font-semibold">
            Outreach Campaign
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            Email and multi-channel outbound
            automation.
          </p>
        </Card>

        <Card className="p-6">
          <h2 className="font-semibold">
            Voice Agent
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            Future outbound calling,
            qualification and barge-in support.
          </p>
        </Card>
      </div>

      <Card className="p-6">
        <h2 className="font-semibold">
          Workflow Status
        </h2>

        <p className="mt-2 text-muted-foreground">
          Authentication integration is the next
          milestone before workflow execution can
          be enabled.
        </p>
      </Card>
    </div>
  );
}