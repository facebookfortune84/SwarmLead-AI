"use client";

import { Button } from "@/components/ui/button";

import {
  Tenant,
} from "@/hooks/use-tenant-list";

import {
  useProvisionTenant,
} from "@/hooks/use-provision-tenant";

interface Props {
  tenants: Tenant[];
}

export function TenantTable({
  tenants,
}: Props) {
  const provision =
    useProvisionTenant();

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="p-4 text-left">
              Name
            </th>

            <th className="p-4 text-left">
              Slug
            </th>

            <th className="p-4 text-left">
              Actions
            </th>
          </tr>
        </thead>

        <tbody>
          {tenants.map(
            (tenant) => (
              <tr
                key={tenant.id}
                className="border-b"
              >
                <td className="p-4">
                  {tenant.name}
                </td>

                <td className="p-4">
                  {
                    tenant.slug
                  }
                </td>

                <td className="p-4">
                  <Button
                    size="sm"
                    onClick={() =>
                      provision.mutate(
                        tenant.id
                      )
                    }
                  >
                    Provision
                  </Button>
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>
    </div>
  );
}