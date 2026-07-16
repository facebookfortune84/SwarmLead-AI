"use client";

import { useMemo } from "react";

import {
  useNotifications,
} from "@/hooks/use-notifications";

import {
  useTenantList,
} from "@/hooks/use-tenant-list";

import {
  useWorkflows,
} from "@/hooks/use-workflows";

import {
  useDashboard,
} from "@/hooks/use-dashboard";

export function useSystemSummary() {
  const dashboard =
    useDashboard();

  const workflows =
    useWorkflows();

  const tenants =
    useTenantList();

  const notifications =
    useNotifications({
      limit: 500,
    });

  return useMemo(
    () => ({
      leads:
        dashboard.data
          ?.leads ?? 0,

      tenants:
        tenants.data
          ?.length ?? 0,

      workflows:
        workflows.data
          ?.length ?? 0,

      notifications:
        notifications.data
          ?.total ?? 0,
    }),
    [
      dashboard.data,
      tenants.data,
      workflows.data,
      notifications.data,
    ]
  );
}