"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { useLeads } from "@/hooks/use-leads";

export default function LeadsPage() {
  const { data, isLoading } =
    useLeads();

  return (
    <AppShell>
      <h1 className="mb-6 text-3xl font-bold">
        Leads
      </h1>

      <Card className="p-6">
        {isLoading ? (
          <p>Loading...</p>
        ) : (
          <pre>
            {JSON.stringify(
              data,
              null,
              2
            )}
          </pre>
        )}
      </Card>
    </AppShell>
  );
}