"use client";

import { AppShell } from "@/components/layout/app-shell";

import {
  TenantManagementConsole,
} from "@/components/tenants/tenant-management-console";

export default function TenantsPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Tenant Management
          </h1>

          <p className="text-muted-foreground">
            Registration,
            provisioning,
            status tracking,
            and tenant operations.
          </p>
        </div>

        <TenantManagementConsole />
      </div>
    </AppShell>
  );
}