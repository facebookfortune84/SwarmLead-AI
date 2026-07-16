"use client";

import { Card } from "@/components/ui/card";

import {
  useTenantProvisionStatus,
} from "@/hooks/use-tenant-provision-status";

interface Props {
  tenantId: string;
}

export function TenantStatusCard({
  tenantId,
}: Props) {
  const {
    data,
    isLoading,
  } =
    useTenantProvisionStatus(
      tenantId
    );

  return (
    <Card className="p-6">
      <h2 className="font-semibold">
        Provision Status
      </h2>

      {isLoading ? (
        <div className="mt-4">
          Loading...
        </div>
      ) : (
        <pre className="mt-4 overflow-auto text-xs">
          {JSON.stringify(
            data,
            null,
            2
          )}
        </pre>
      )}
    </Card>
  );
}