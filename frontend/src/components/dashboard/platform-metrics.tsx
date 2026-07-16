"use client";

import { Card } from "@/components/ui/card";

interface Props {
  leads: number;

  tenants: number;

  workflows: number;

  notifications: number;
}

export function PlatformMetrics({
  leads,
  tenants,
  workflows,
  notifications,
}: Props) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Card className="p-6">
        <div className="text-sm text-muted-foreground">
          Leads
        </div>

        <div className="mt-2 text-3xl font-bold">
          {leads}
        </div>
      </Card>

      <Card className="p-6">
        <div className="text-sm text-muted-foreground">
          Tenants
        </div>

        <div className="mt-2 text-3xl font-bold">
          {tenants}
        </div>
      </Card>

      <Card className="p-6">
        <div className="text-sm text-muted-foreground">
          Workflows
        </div>

        <div className="mt-2 text-3xl font-bold">
          {workflows}
        </div>
      </Card>

      <Card className="p-6">
        <div className="text-sm text-muted-foreground">
          Notifications
        </div>

        <div className="mt-2 text-3xl font-bold">
          {notifications}
        </div>
      </Card>
    </div>
  );
}