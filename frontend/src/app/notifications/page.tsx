"use client";

import { AppShell } from "@/components/layout/app-shell";

import {
  NotificationCenter,
} from "@/components/notifications/notification-center";

export default function NotificationsPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">
            Notifications
          </h1>

          <p className="text-muted-foreground">
            Platform alerts,
            workflow status,
            outreach activity,
            and tenant events.
          </p>
        </div>

        <NotificationCenter />
      </div>
    </AppShell>
  );
}