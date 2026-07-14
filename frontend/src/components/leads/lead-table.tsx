"use client";

import { Lead } from "@/types/lead";

import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";

import { LeadStatusBadge } from "./lead-status-badge";

interface Props {
  leads: Lead[];
  onSelect: (
    lead: Lead
  ) => void;
}

export function LeadTable({
  leads,
  onSelect,
}: Props) {
  return (
    <div className="rounded-xl border bg-card">
      <Table>
        <TableHeader className="sticky top-0 z-10 bg-background">
          <TableRow>
            <TableHead>
              Name
            </TableHead>

            <TableHead>
              Email
            </TableHead>

            <TableHead>
              Company
            </TableHead>

            <TableHead>
              Owner
            </TableHead>

            <TableHead>
              Score
            </TableHead>

            <TableHead>
              Status
            </TableHead>

            <TableHead>
              Created
            </TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          {leads.map((lead) => (
            <TableRow
              key={lead.id}
              onClick={() =>
                onSelect(lead)
              }
              className="cursor-pointer"
            >
              <TableCell>
                {lead.name ?? "-"}
              </TableCell>

              <TableCell>
                {lead.email}
              </TableCell>

              <TableCell>
                {lead.company ??
                  "-"}
              </TableCell>

              <TableCell>
                {lead.owner ??
                  "-"}
              </TableCell>

              <TableCell>
                {lead.score ??
                  "-"}
              </TableCell>

              <TableCell>
                <LeadStatusBadge
                  status={
                    lead.status
                  }
                />
              </TableCell>

              <TableCell>
                {new Date(
                  lead.created_at
                ).toLocaleDateString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}