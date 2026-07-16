"use client";

import { User } from "@/types/user";

interface Props {
  users: User[];
}

export function AdminStats({
  users,
}: Props) {
  const active =
    users.filter(
      (u) =>
        u.is_active
    ).length;

  const inactive =
    users.filter(
      (u) =>
        !u.is_active
    ).length;

  const admins =
    users.filter(
      (u) =>
        u.role ===
          "admin" ||
        u.role ===
          "superadmin"
    ).length;

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <div className="rounded-lg border p-4">
        <div className="text-sm text-muted-foreground">
          Active Users
        </div>

        <div className="text-3xl font-bold">
          {active}
        </div>
      </div>

      <div className="rounded-lg border p-4">
        <div className="text-sm text-muted-foreground">
          Inactive Users
        </div>

        <div className="text-3xl font-bold">
          {inactive}
        </div>
      </div>

      <div className="rounded-lg border p-4">
        <div className="text-sm text-muted-foreground">
          Admins
        </div>

        <div className="text-3xl font-bold">
          {admins}
        </div>
      </div>
    </div>
  );
}