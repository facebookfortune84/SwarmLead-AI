"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  NotificationResponse,
} from "@/types/notification";

interface Options {
  skip?: number;

  limit?: number;

  unreadOnly?: boolean;
}

export function useNotifications(
  options: Options = {}
) {
  const {
    skip = 0,
    limit = 50,
    unreadOnly = false,
  } = options;

  return useQuery<NotificationResponse>({
    queryKey: [
      "notifications",
      skip,
      limit,
      unreadOnly,
    ],

    queryFn: async () => {
      const response =
        await api.get(
          "/api/notifications",
          {
            params: {
              skip,
              limit,
              unread_only:
                unreadOnly,
            },
          }
        );

      return response.data;
    },

    staleTime: 30000,

    retry: 1,
  });
}