"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

async function fetchDashboard() {
  const [leadsResponse, tenantsResponse] =
    await Promise.all([
      api.get("/api/leads/"),
      api.get("/api/tenants"),
    ]);

  const leads =
    leadsResponse.data?.leads ?? [];

  const tenants =
    tenantsResponse.data?.tenants ?? [];

  return {
    leads: leads.length,

    tenants: tenants.length,

    qualifiedLeads: leads.filter(
      (lead: { status?: string }) =>
        lead.status ===
        "QUALIFIED"
    ).length,

    customers: leads.filter(
      (lead: { status?: string }) =>
        lead.status ===
        "CUSTOMER"
    ).length,

    workflows: "Locked",

    tickets: 0,
  };
}

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
    retry: false,
    staleTime: 60_000,
  });
}