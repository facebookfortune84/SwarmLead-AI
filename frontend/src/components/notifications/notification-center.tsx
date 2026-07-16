"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import {
  useNotifications,
} from "@/hooks/use-notifications";

import {
  useMarkNotificationRead,
} from "@/hooks/use-mark-notification-read";

import {
  useMarkAllRead,
} from "@/hooks/use-mark-all-read";

import {
  useDeleteNotification,
} from "@/hooks/use-delete-notification";

export function NotificationCenter() {
  const {
    data,
    isLoading,
  } =
    useNotifications();

  const markRead =
    useMarkNotificationRead();

  const markAllRead =
    useMarkAllRead();

  const deleteNotification =
    useDeleteNotification();

  if (isLoading) {
    return (
      <Card className="p-6">
        Loading notifications...
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">
            Notifications
          </h2>

          <p className="text-sm text-muted-foreground">
            {data?.total ?? 0}
            {" "}
            notifications
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() =>
            markAllRead.mutate()
          }
        >
          Mark All Read
        </Button>
      </div>

      {data?.items.length ===
      0 ? (
        <div className="rounded-lg border p-6 text-center text-muted-foreground">
          No notifications.
        </div>
      ) : (
        <div className="space-y-3">
          {data?.items.map(
            (
              notification
            ) => (
              <div
                key={
                  notification.id
                }
                className={`rounded-lg border p-4 ${
                  notification.is_read
                    ? ""
                    : "border-primary"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-medium">
                      {
                        notification.title
                      }
                    </h3>

                    <p className="mt-1 text-sm text-muted-foreground">
                      {
                        notification.message
                      }
                    </p>

                    <div className="mt-2 text-xs text-muted-foreground">
                      {
                        notification.type
                      }
                    </div>

                    <div className="text-xs text-muted-foreground">
                      {
                        notification.created_at
                      }
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {!notification.is_read && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          markRead.mutate(
                            notification.id
                          )
                        }
                      >
                        Read
                      </Button>
                    )}

                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() =>
                        deleteNotification.mutate(
                          notification.id
                        )
                      }
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      )}
    </Card>
  );
}