"use client";

import { Card } from "@/components/ui/card";

const agents = [
  {
    name:
      "Discovery Agent",
    type:
      "DISCOVERY",
  },

  {
    name:
      "Qualification Agent",
    type:
      "QUALIFICATION",
  },

  {
    name:
      "Outreach Agent",
    type:
      "OUTREACH",
  },

  {
    name:
      "Voice Agent",
    type: "VOICE",
  },
];

export function AgentRegistry() {
  return (
    <Card className="p-6">
      <h2 className="font-semibold">
        Agent Registry
      </h2>

      <div className="mt-4 space-y-3">
        {agents.map(
          (agent) => (
            <div
              key={agent.name}
              className="rounded-lg border p-3"
            >
              <div className="font-medium">
                {agent.name}
              </div>

              <div className="text-sm text-muted-foreground">
                {agent.type}
              </div>
            </div>
          )
        )}
      </div>
    </Card>
  );
}