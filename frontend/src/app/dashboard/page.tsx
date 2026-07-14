"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { useDashboard } from "@/hooks/use-dashboard";

export default function DashboardPage() {
  const { data, isLoading } =
    useDashboard();

  return (
    <AppShell>
      <h1 className="mb-6 text-3xl font-bold">
        Dashboard
      </h1>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="p-6">
          <h3 className="text-sm text-muted-foreground">
            Leads
          </h3>

          <p className="mt-2 text-3xl font-bold">
            {isLoading
              ? "..."
              : data?.leads}
          </p>
        </Card>

        <Card className="p-6">
          <h3 className="text-sm text-muted-foreground">
            Tickets
          </h3>

          <p className="mt-2 text-3xl font-bold">
            {isLoading
              ? "..."
              : data?.tickets}
          </p>
        </Card>

        <Card className="p-6">
          <h3 className="text-sm text-muted-foreground">
            Workflows
          </h3>

          <p className="mt-2 text-3xl font-bold">
            {isLoading
              ? "..."
              : String(data?.workflows)}
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
    </AppShell>
  );
}