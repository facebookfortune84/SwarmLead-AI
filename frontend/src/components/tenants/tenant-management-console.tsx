"use client";

import { Card } from "@/components/ui/card";

import {
  useTenantList,
} from "@/hooks/use-tenant-list";

import {
  CreateTenantForm,
} from "./create-tenant-form";

import {
  TenantTable,
} from "./tenant-table";

export function TenantManagementConsole() {
  const {
    data = [],
    isLoading,
  } =
    useTenantList();

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="mb-4 font-semibold">
          Register Tenant
        </h2>

        <CreateTenantForm />
      </Card>

      <Card className="p-6">
        <h2 className="mb-4 font-semibold">
          Existing Tenants
        </h2>

        {isLoading ? (
          <div>
            Loading...
          </div>
        ) : (
          <TenantTable
            tenants={data}
          />
        )}
      </Card>
    </div>
  );
}