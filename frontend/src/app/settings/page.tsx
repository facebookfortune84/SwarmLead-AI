"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Settings
          </h1>

          <p className="text-muted-foreground">
            Platform configuration, AI agents,
            integrations, and future voice settings.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card className="p-6">
            <h2 className="font-semibold">
              CRM Configuration
            </h2>

            <p className="mt-2 text-sm text-muted-foreground">
              Lead lifecycle and pipeline settings.
            </p>
          </Card>

          <Card className="p-6">
            <h2 className="font-semibold">
              Agent Configuration
            </h2>

            <p className="mt-2 text-sm text-muted-foreground">
              Discovery, qualification and outreach agents.
            </p>
          </Card>

          <Card className="p-6">
            <h2 className="font-semibold">
              Voice Settings
            </h2>

            <p className="mt-2 text-sm text-muted-foreground">
              Future voice provider and barge-in controls.
            </p>
          </Card>
        </div>

        <Card className="p-6">
          <h2 className="font-semibold">
            Platform Roadmap
          </h2>

          <div className="mt-4 space-y-3">
            <div className="rounded-lg border p-3">
              ✅ CRM Foundation
            </div>

            <div className="rounded-lg border p-3">
              ✅ Lead Intelligence
            </div>

            <div className="rounded-lg border p-3">
              ⏳ Authentication
            </div>

            <div className="rounded-lg border p-3">
              ⏳ Workflow Execution
            </div>

            <div className="rounded-lg border p-3">
              ⏳ AI Agents
            </div>

            <div className="rounded-lg border p-3">
              ⏳ Voice + Human Barge-In
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}