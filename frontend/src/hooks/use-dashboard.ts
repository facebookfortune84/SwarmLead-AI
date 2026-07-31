"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface WorkflowItem {
  id: string;
  name: string;
  status: string;
}

async function fetchDashboard() {
  const [leadsResponse, tenantsResponse, workflowsResponse, notificationsResponse] =
    await Promise.all([
      api.get("/api/leads/"),
      api.get("/api/tenants"),
      api.get("/api/workflows/"),
      api.get("/api/notifications", { params: { limit: 5 } }),
    ]);

  const leads = leadsResponse.data?.leads ?? [];
  const tenants = tenantsResponse.data?.tenants ?? [];
  const workflows: WorkflowItem[] = workflowsResponse.data?.items ?? [];
  const notifications = notificationsResponse.data?.items ?? [];

  return {
    leads: leads.length,
    tenants: tenants.length,
    qualifiedLeads: leads.filter((lead: { status?: string }) => lead.status === "QUALIFIED").length,
    customers: leads.filter((lead: { status?: string }) => lead.status === "CUSTOMER").length,
    workflows,
    runningWorkflows: workflows.filter((w) => w.status === "running").length,
    unreadNotifications: notifications.filter((n: { is_read?: boolean }) => !n.is_read).length,
  };
}

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
    retry: false,
    staleTime: 60_000,
    refetchInterval: 30_000,
  });
}
