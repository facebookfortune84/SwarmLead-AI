"use client";

import { Card } from "@/components/ui/card";

import {
  useUsers,
} from "@/hooks/use-users";

export function AdminDashboardCard() {
  const {
    data = [],
  } = useUsers();

  return (
    <Card className="p-6">
      <h2 className="font-semibold">
        User Administration
      </h2>

      <div className="mt-4">
        <div className="text-sm text-muted-foreground">
          Total Users
        </div>

        <div className="text-3xl font-bold">
          {data.length}
        </div>
      </div>
    </Card>
  );
}