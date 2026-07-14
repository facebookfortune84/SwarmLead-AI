"use client";

import { Lead } from "@/types/lead";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

import { LeadStatusBadge } from "./lead-status-badge";
import { LeadActions } from "./lead-actions";
import { LeadActivityFeed } from "./lead-activity-feed";

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
      <SheetContent className="overflow-y-auto">
        <SheetHeader>
          <SheetTitle>
            Lead Profile
          </SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          <div>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">
                  {lead.name ??
                    "Unknown Lead"}
                </h2>

                <div className="text-sm text-muted-foreground">
                  {lead.email}
                </div>
              </div>

              <LeadStatusBadge
                status={lead.status}
              />
            </div>
          </div>

          <LeadActions lead={lead} />

          <div className="rounded-lg border p-4">
            <div className="mb-3 text-sm font-semibold">
              Company
            </div>

            <div>
              {display(
                lead.company
              )}
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-3 text-sm font-semibold">
              Ownership
            </div>

            <div className="space-y-2 text-sm">
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
                  Agent Source:
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
            <div className="mb-3 text-sm font-semibold">
              Lead Intelligence
            </div>

            <div className="space-y-2 text-sm">
              <div>
                <strong>
                  Lead Score:
                </strong>{" "}
                {display(
                  lead.score
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
                  Last Contact:
                </strong>{" "}
                {display(
                  lead.last_contacted
                )}
              </div>
            </div>
          </div>

          <LeadActivityFeed
            lead={lead}
          />

          <div className="rounded-lg border p-4">
            <div className="mb-3 text-sm font-semibold">
              Tags
            </div>

            {lead.tags?.length ? (
              <div className="flex flex-wrap gap-2">
                {lead.tags.map(
                  (tag) => (
                    <span
                      key={tag}
                      className="
                        rounded-full
                        border
                        px-2
                        py-1
                        text-xs
                      "
                    >
                      {tag}
                    </span>
                  )
                )}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                No tags assigned
              </div>
            )}
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-3 text-sm font-semibold">
              Notes
            </div>

            <div className="text-sm">
              {display(
                lead.notes
              )}
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="mb-3 text-sm font-semibold">
              Audit Information
            </div>

            <div className="space-y-2 text-sm">
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