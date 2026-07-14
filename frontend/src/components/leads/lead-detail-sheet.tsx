"use client";

import { Lead } from "@/types/lead";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

import { Badge } from "@/components/ui/badge";
import { LeadActions } from "./lead-actions";

interface Props {
  lead: Lead | null;
  open: boolean;
  onOpenChange: (
    open: boolean
  ) => void;
}

function display(
  value?: string | number | null
) {
  return value ?? "-";
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
      <SheetContent
        className="overflow-y-auto"
      >
        <SheetHeader>
          <SheetTitle>
            Lead Profile
          </SheetTitle>
              </SheetHeader>

        
        <div className="mt-4">
            <LeadActions lead={lead} />
        </div>

        <div className="mt-6 space-y-6">
          <div>
            <h2 className="text-xl font-bold">
              {lead.name ??
                "Unknown Lead"}
            </h2>

            <div className="text-sm text-muted-foreground">
              {lead.email}
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-2 text-sm font-semibold">
              Status
            </div>

            <Badge>
              {lead.status}
            </Badge>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-2 text-sm font-semibold">
              Company
            </div>

            <div>
              {display(
                lead.company
              )}
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-2 text-sm font-semibold">
              Ownership
            </div>

            <div className="text-sm space-y-1">
              <div>
                <strong>
                  Owner:
                </strong>{" "}
                {display(
                  lead.owner
                )}
              </div>

              <div>
                <strong>
                  Source:
                </strong>{" "}
                {display(
                  lead.agent_source
                )}
              </div>

              <div>
                <strong>
                  Discovery Agent:
                </strong>{" "}
                {display(
                  lead.discovery_agent
                )}
              </div>
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-2 text-sm font-semibold">
              Activity
            </div>

            <div className="text-sm space-y-1">
              <div>
                <strong>
                  Last Contact:
                </strong>{" "}
                {display(
                  lead.last_contacted
                )}
              </div>

              <div>
                <strong>
                  Next Action:
                </strong>{" "}
                {display(
                  lead.next_action
                )}
              </div>

              <div>
                <strong>
                  Lead Score:
                </strong>{" "}
                {display(
                  lead.score
                )}
              </div>
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-2 text-sm font-semibold">
              Tags
            </div>

            <div className="flex flex-wrap gap-2">
              {lead.tags?.length ? (
                lead.tags.map(
                  (tag) => (
                    <Badge
                      key={tag}
                      variant="outline"
                    >
                      {tag}
                    </Badge>
                  )
                )
              ) : (
                <span className="text-sm text-muted-foreground">
                  No tags
                </span>
              )}
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-2 text-sm font-semibold">
              Notes
            </div>

            <div className="text-sm">
              {display(
                lead.notes
              )}
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-2 text-sm font-semibold">
              Audit
            </div>

            <div className="text-sm space-y-1">
              <div>
                <strong>ID:</strong>{" "}
                {lead.id}
              </div>

              <div>
                <strong>
                  Created:
                </strong>{" "}
                {new Date(
                  lead.created_at
                ).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}