"use client";

import { AppShell } from "@/components/layout/app-shell";

import {
  PermissionGate,
} from "@/components/auth/permission-gate";

import {
  Permission,
} from "@/types/rbac";

import {
  AdminDashboardCard,
} from "@/components/admin/admin-dashboard-card";

import {
  SystemHealthCard,
} from "@/components/admin/system-health-card";

import {
  AdminNavigation,
} from "@/components/admin/admin-navigation";

export default function AdminPage() {
  return (
    <AppShell>
      <PermissionGate
        permission={
          Permission.READ_ALL_USERS
        }
      >
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">
              Admin Console
            </h1>

            <p className="text-muted-foreground">
              Platform administration,
              monitoring,
              security,
              and operations.
            </p>
          </div>

          <AdminNavigation />

          <div className="grid gap-4 lg:grid-cols-2">
            <AdminDashboardCard />

            <SystemHealthCard />
          </div>
        </div>
      </PermissionGate>
    </AppShell>
  );
}