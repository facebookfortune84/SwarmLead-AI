"use client";

import { AppShell } from "@/components/layout/app-shell";

import {
  PermissionGate,
} from "@/components/auth/permission-gate";

import {
  Permission,
} from "@/types/rbac";

import {
  UserManagementConsole,
} from "@/components/admin/user-management-console";

export default function UsersPage() {
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
              User Administration
            </h1>

            <p className="text-muted-foreground">
              User lifecycle,
              permissions,
              access control,
              and account management.
            </p>
          </div>

          <UserManagementConsole />
        </div>
      </PermissionGate>
    </AppShell>
  );
}