"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNotifications } from "@/hooks/use-notifications";
import { useMarkNotificationRead } from "@/hooks/use-mark-notification-read";
import { useMarkAllRead } from "@/hooks/use-mark-all-read";
import { useDeleteNotification } from "@/hooks/use-delete-notification";
import { Bell, Loader2, XCircle, Inbox, RefreshCw, CheckCheck } from "lucide-react";
import { motion } from "framer-motion";

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

const TYPE_COLORS: Record<string, string> = {
  info: "text-blue-400",
  warning: "text-amber-400",
  error: "text-red-400",
  success: "text-emerald-400",
};

export function NotificationCenter() {
  const { data, isLoading, isError, refetch } = useNotifications();
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllRead();
  const deleteNotification = useDeleteNotification();

  if (isLoading) {
    return (
      <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
        <div className="flex items-center justify-center py-16 text-white/40">
          <Loader2 className="w-5 h-5 text-indigo-400 animate-spin mr-2" />
          Loading notifications...
        </div>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
        <div className="flex flex-col items-center justify-center py-16">
          <XCircle className="w-10 h-10 text-red-400 mb-3" />
          <p className="text-sm font-medium text-red-300">Failed to load notifications</p>
          <p className="text-xs text-white/40 mt-1 mb-4">Please sign in or try again later.</p>
          <Button size="sm" variant="outline" onClick={() => refetch()}>
            <RefreshCw className="w-3.5 h-3.5 mr-2" /> Retry
          </Button>
        </div>
      </Card>
    );
  }

  const items = data?.items ?? [];
  const unreadCount = items.filter((n) => !n.is_read).length;
  const anyPending = markRead.isPending || markAllRead.isPending || deleteNotification.isPending;

  return (
    <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-semibold text-white">Notifications</h2>
          </div>
          <p className="mt-1 text-sm text-white/50">
            {data?.total ?? 0} total{unreadCount > 0 ? ` · ${unreadCount} unread` : ""}
          </p>
        </div>

        {items.length > 0 && (
          <Button variant="outline" size="sm" onClick={() => markAllRead.mutate()} disabled={anyPending || unreadCount === 0}>
            <CheckCheck className="w-3.5 h-3.5 mr-2" />
            Mark All Read
          </Button>
        )}
      </div>

      {markRead.isError && (
        <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-300">
          Failed to update notification.
        </div>
      )}
      {deleteNotification.isError && (
        <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-300">
          Failed to delete notification.
        </div>
      )}

      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 rounded-xl bg-white/5 border border-white/[0.06]">
          <Inbox className="w-10 h-10 text-white/20 mb-3" />
          <p className="text-sm font-medium text-white/60">No notifications</p>
          <p className="mt-1 text-xs text-white/40">You're all caught up.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((notification, i) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
              className={`rounded-xl border p-4 transition-colors ${
                notification.is_read
                  ? "border-white/[0.06] bg-white/[0.02]"
                  : "border-indigo-500/30 bg-indigo-500/[0.06]"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    {!notification.is_read && <div className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />}
                    <h3 className="font-medium text-white truncate">{notification.title}</h3>
                  </div>
                  <p className="mt-1 text-sm text-white/60">{notification.message}</p>
                  <div className="mt-2 flex items-center gap-3 text-xs">
                    <span className={`${TYPE_COLORS[notification.type] ?? "text-white/50"} capitalize`}>
                      {notification.type}
                    </span>
                    <span className="text-white/30">·</span>
                    <span className="text-white/40">{formatDate(notification.created_at)}</span>
                  </div>
                </div>

                <div className="flex shrink-0 gap-2">
                  {!notification.is_read && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => markRead.mutate(notification.id)}
                      disabled={anyPending}
                    >
                      Read
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => deleteNotification.mutate(notification.id)}
                    disabled={anyPending}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </Card>
  );
}
