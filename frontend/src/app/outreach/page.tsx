"use client";

import { AppShell } from "@/components/layout/app-shell";

import { Card } from "@/components/ui/card";

import {
  OutreachForm,
} from "@/components/outreach/outreach-form";

import {
  CampaignForm,
} from "@/components/outreach/campaign-form";

import {
  CampaignTemplateGrid,
} from "@/components/outreach/campaign-template-grid";

export default function OutreachPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Outreach Center
          </h1>

          <p className="text-muted-foreground">
            Campaign execution,
            lead engagement,
            AI-assisted prospecting,
            and future voice automation.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Campaigns
            </div>

            <div className="mt-2 text-3xl font-bold">
              Live
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Outreach
            </div>

            <div className="mt-2 text-3xl font-bold">
              Ready
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Workflow Engine
            </div>

            <div className="mt-2 text-3xl font-bold">
              Online
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Voice
            </div>

            <div className="mt-2 text-3xl font-bold">
              Planned
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h2 className="mb-4 font-semibold">
            Campaign Templates
          </h2>

          <CampaignTemplateGrid />
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 font-semibold">
            Single Outreach
          </h2>

          <OutreachForm />
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 font-semibold">
            Campaign Broadcast
          </h2>

          <CampaignForm />
        </Card>
      </div>
    </AppShell>
  );
}