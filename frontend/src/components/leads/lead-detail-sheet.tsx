"use client";

import { Lead } from "@/types/lead";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

interface Props {
  lead: Lead | null;
  open: boolean;
  onOpenChange: (
    open: boolean
  ) => void;
}

export function LeadDetailSheet({
  lead,
  open,
  onOpenChange,
}: Props) {
  if (!lead) return null;

  return (
    <Sheet
      open={open}
      onOpenChange={onOpenChange}
    >
      <SheetContent>
        <SheetHeader>
          <SheetTitle>
            Lead Details
          </SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          <div>
            <div className="text-xs text-muted-foreground">
              ID
            </div>

            <div>{lead.id}</div>
          </div>

          <div>
            <div className="text-xs text-muted-foreground">
              Name
            </div>

            <div>
              {lead.name ?? "-"}
            </div>
          </div>

          <div>
            <div className="text-xs text-muted-foreground">
              Email
            </div>

            <div>{lead.email}</div>
          </div>

          <div>
            <div className="text-xs text-muted-foreground">
              Company
            </div>

            <div>
              {lead.company ?? "-"}
            </div>
          </div>

          <div>
            <div className="text-xs text-muted-foreground">
              Status
            </div>

            <div>{lead.status}</div>
          </div>

          <div>
            <div className="text-xs text-muted-foreground">
              Created
            </div>

            <div>
              {new Date(
                lead.created_at
              ).toLocaleString()}
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}