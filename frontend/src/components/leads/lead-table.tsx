"use client";

import {
  LeadTicketButton,
} from "./lead-ticket-button";

import {
  Lead,
} from "@/types/lead";

interface Props {
  leads: Lead[];
}

export function LeadTable({
  leads,
}: Props) {
  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="p-4 text-left">
              Email
            </th>

            <th className="p-4 text-left">
              Name
            </th>

            <th className="p-4 text-left">
              Company
            </th>

            <th className="p-4 text-left">
              Actions
            </th>
          </tr>
        </thead>

        <tbody>
          {leads.map(
            (
              lead
            ) => (
              <tr
                key={lead.id}
                className="border-b"
              >
                <td className="p-4">
                  {lead.email}
                </td>

                <td className="p-4">
                  {
                    lead.name ??
                    "-"
                  }
                </td>

                <td className="p-4">
                  {
                    lead.company ??
                    "-"
                  }
                </td>

                <td className="p-4">
                  <LeadTicketButton
                    leadId={
                      lead.id
                    }
                  />
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>
    </div>
  );
}