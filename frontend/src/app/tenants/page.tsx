"use client";

import { AppShell } from "@/components/layout/app-shell";

import { Card } from "@/components/ui/card";

import { useTenants } from "@/hooks/use-tenants";

export default function TenantsPage() {
  const {
    data = [],
    isLoading,
  } = useTenants();

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Tenants
          </h1>

          <p className="text-muted-foreground">
            Multi-tenant account management.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Total Tenants
            </div>

            <div className="mt-2 text-3xl font-bold">
              {isLoading
                ? "..."
                : data.length}
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Active
            </div>

            <div className="mt-2 text-3xl font-bold">
              {isLoading
                ? "..."
                : data.length}
            </div>
          </Card>

          <Card className="p-6">
            <div className="text-sm text-muted-foreground">
              Provisioned
            </div>

            <div className="mt-2 text-3xl font-bold">
              {isLoading
                ? "..."
                : data.length}
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h2 className="mb-4 font-semibold">
            Tenant Directory
          </h2>

          {isLoading ? (
            <div>
              Loading tenants...
            </div>
          ) : data.length === 0 ? (
            <div className="text-muted-foreground">
              No tenants found.
            </div>
          ) : (
            <div className="space-y-3">
              {data.map(
                (
                  tenant: { id: string; name?: string; slug?: string }
                ) => (
                  <div
                    key={
                      tenant.id
                    }
                    className="rounded-lg border p-4"
                  >
                    <div className="font-medium">
                      {tenant.name ??
                        tenant.id}
                    </div>

                    <div className="text-sm text-muted-foreground">
                      {
                        tenant.slug
                      }
                    </div>
                  </div>
                )
              )}
            </div>
          )}
        </Card>
      </div>
    </AppShell>
  );
}