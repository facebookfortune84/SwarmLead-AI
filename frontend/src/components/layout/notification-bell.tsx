"use client";

import { Bell } from "lucide-react";

import { Button } from "@/components/ui/button";

import {
  useNotifications,
} from "@/hooks/use-notifications";

interface Props {
  onOpen: () => void;
}

export function NotificationBell({
  onOpen,
}: Props) {
  const {
    data,
  } =
    useNotifications({
      unreadOnly: true,
    });

  const unreadCount =
    data?.items?.length ?? 0;

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onOpen}
      className="relative"
    >
      <Bell className="h-5 w-5" />

      {unreadCount >
        0 && (
        <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-xs text-white">
          {unreadCount >
          99
            ? "99+"
            : unreadCount}
        </span>
      )}
    </Button>
  );
}