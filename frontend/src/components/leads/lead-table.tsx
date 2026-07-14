"use client";

import { Lead } from "@/types/lead";
import { LeadStatusBadge } from "./lead-status-badge";

interface Props {
  leads: Lead[];
  onSelect: (lead: Lead) => void;
}

export function LeadTable({
  leads,
  onSelect,
}: Props) {
  return (
    <div className="overflow-hidden rounded-lg border">
      <table className="w-full text-sm">
        <thead className="border-b bg-muted/20">
          <tr>
            <th className="p-3 text-left">
              Name
            </th>

            <th className="p-3 text-left">
              Email
            </th>

            <th className="p-3 text-left">
              Company
            </th>

            <th className="p-3 text-left">
              Status
            </th>

            <th className="p-3 text-left">
              Created
            </th>
          </tr>
        </thead>

        <tbody>
          {leads.map((lead) => (
            <tr
              key={lead.id}
              onClick={() =>
                onSelect(lead)
              }
              className="
                cursor-pointer
                border-b
                transition-colors
                hover:bg-muted/50
              "
            >
              <td className="p-3">
                {lead.name ?? "-"}
              </td>

              <td className="p-3">
                {lead.email}
              </td>

              <td className="p-3">
                {lead.company ?? "-"}
              </td>

              <td className="p-3">
                <LeadStatusBadge
                  status={lead.status}
                />
              </td>

              <td className="p-3">
                {new Date(
                  lead.created_at
                ).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

