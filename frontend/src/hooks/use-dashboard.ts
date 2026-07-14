"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

async function fetchDashboard() {
  const [leadsResponse, tenantsResponse] =
    await Promise.all([
      api.get("/api/leads/"),
      api.get("/api/tenants"),
    ]);

  return {
    leads:
      leadsResponse.data?.leads?.length ?? 0,

    tenants:
      tenantsResponse.data?.tenants?.length ?? 0,

    workflows: "Locked",

    tickets: 0,
  };
}

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
    retry: false,
  });
}