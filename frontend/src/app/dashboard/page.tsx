"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

import { useDashboard } from "@/hooks/use-dashboard";

export default function DashboardPage() {
  const {
    data,
    isLoading,
  } = useDashboard();

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Dashboard
          </h1>

          <p className="text-muted-foreground">
            Lead intelligence,
            workflows,
            outreach,
            voice agents,
            and tenant operations.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card className="p-6">
            <h3 className="text-sm text-muted-foreground">
              Total Leads
            </h3>

            <p className="mt-2 text-3xl font-bold">
              {isLoading
                ? "..."
                : data?.leads}
            </p>
          </Card>

          <Card className="p-6">
            <h3 className="text-sm text-muted-foreground">
              Qualified Leads
            </h3>

            <p className="mt-2 text-3xl font-bold">
              {isLoading
                ? "..."
                : data?.qualifiedLeads}
            </p>
          </Card>

          <Card className="p-6">
            <h3 className="text-sm text-muted-foreground">
              Customers
            </h3>

            <p className="mt-2 text-3xl font-bold">
              {isLoading
                ? "..."
                : data?.customers}
            </p>
          </Card>

          <Card className="p-6">
            <h3 className="text-sm text-muted-foreground">
              Tenants
            </h3>

            <p className="mt-2 text-3xl font-bold">
              {isLoading
                ? "..."
                : data?.tenants}
            </p>
          </Card>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="p-6">
            <h2 className="font-semibold">
              AI Agent Activity
            </h2>

            <div className="mt-4 space-y-3 text-sm">
              <div className="rounded-lg border p-3">
                Lead Discovery Agent
                <span className="float-right text-muted-foreground">
                  Ready
                </span>
              </div>

              <div className="rounded-lg border p-3">
                Outreach Agent
                <span className="float-right text-muted-foreground">
                  Planned
                </span>
              </div>

              <div className="rounded-lg border p-3">
                Voice Agent
                <span className="float-right text-muted-foreground">
                  Planned
                </span>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="font-semibold">
              Workflow Center
            </h2>

            <div className="mt-4 space-y-3 text-sm">
              <div className="rounded-lg border p-3">
                Qualification Workflow
              </div>

              <div className="rounded-lg border p-3">
                Outreach Workflow
              </div>

              <div className="rounded-lg border p-3">
                Voice Escalation Workflow
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h2 className="font-semibold">
            Platform Status
          </h2>

          <div className="mt-4 grid gap-4 sm:grid-cols-4">
            <div>
              <div className="text-sm text-muted-foreground">
                CRM
              </div>

              <div className="font-semibold text-green-600">
                Online
              </div>
            </div>

            <div>
              <div className="text-sm text-muted-foreground">
                API
              </div>

              <div className="font-semibold text-green-600">
                Online
              </div>
            </div>

            <div>
              <div className="text-sm text-muted-foreground">
                Workflows
              </div>

              <div className="font-semibold text-yellow-500">
                Auth Required
              </div>
            </div>

            <div>
              <div className="text-sm text-muted-foreground">
                Voice
              </div>

              <div className="font-semibold text-muted-foreground">
                Planned
              </div>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}