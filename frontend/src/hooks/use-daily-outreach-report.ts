"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

import {
  DailyOutreachMetric,
} from "@/types/analytics";

export function useDailyOutreachReport(
  startDate: string,
  endDate: string
) {
  return useQuery<
    DailyOutreachMetric[]
  >({
    queryKey: [
      "daily-outreach-report",
      startDate,
      endDate,
    ],

    enabled:
      Boolean(
        startDate
      ) &&
      Boolean(
        endDate
      ),

    queryFn: async () => {
      const response =
        await api.get(
          "/api/outreach/reports/daily",
          {
            params: {
              start_date:
                startDate,

              end_date:
                endDate,
            },
          }
        );

      return (
        response.data ??
        []
      );
    },

    staleTime:
      1000 * 60,

    retry: 1,
  });
}