"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function OutreachPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Outreach Center
          </h1>

          <p className="text-muted-foreground">
            Multi-channel campaign management,
            AI outreach agents, workflow automation,
            and future voice operations.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Active Campaigns
            </div>

            <div className="mt-2 text-3xl font-bold">
              0
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Emails Sent
            </div>

            <div className="mt-2 text-3xl font-bold">
              0
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Voice Calls
            </div>

            <div className="mt-2 text-3xl font-bold">
              0
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Replies
            </div>

            <div className="mt-2 text-3xl font-bold">
              0
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold">
                Campaign Templates
              </h2>

              <p className="text-sm text-muted-foreground">
                Reusable outreach patterns.
              </p>
            </div>

            <Button>
              Create Campaign
            </Button>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <Card className="p-4">
              <h3 className="font-medium">
                Cold Outreach
              </h3>

              <p className="mt-2 text-sm text-muted-foreground">
                Initial contact sequence.
              </p>
            </Card>

            <Card className="p-4">
              <h3 className="font-medium">
                Follow-Up
              </h3>

              <p className="mt-2 text-sm text-muted-foreground">
                Re-engagement workflow.
              </p>
            </Card>

            <Card className="p-4">
              <h3 className="font-medium">
                Voice Qualification
              </h3>

              <p className="mt-2 text-sm text-muted-foreground">
                Future AI voice workflow.
              </p>
            </Card>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="font-semibold">
            AI Outreach Roadmap
          </h2>

          <div className="mt-4 space-y-3 text-sm">
            <div className="rounded-lg border p-3">
              ✅ Lead CRM Foundation
            </div>

            <div className="rounded-lg border p-3">
              ✅ Workflow Launch Infrastructure
            </div>

            <div className="rounded-lg border p-3">
              ⏳ Campaign Engine
            </div>

            <div className="rounded-lg border p-3">
              ⏳ AI Outreach Agents
            </div>

            <div className="rounded-lg border p-3">
              ⏳ Voice Agents
            </div>

            <div className="rounded-lg border p-3">
              ⏳ Human Barge-In Console
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}