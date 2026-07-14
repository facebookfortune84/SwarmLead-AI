"use client";

import { Lead } from "@/types/lead";

interface Props {
  lead: Lead;
}

export function LeadActivityFeed({
  lead,
}: Props) {
  const events = [
    {
      title:
        "Lead Created",
      value:
        lead.created_at,
    },

    {
      title:
        "Last Contact",
      value:
        lead.last_contacted,
    },

    {
      title:
        "Next Action",
      value:
        lead.next_action,
    },
  ].filter(Boolean);

  return (
    <div className="rounded-lg border p-4">
      <div className="mb-3 text-sm font-semibold">
        Activity Timeline
      </div>

      <div className="space-y-3">
        {events.map(
          (event, index) => (
            <div
              key={index}
              className="border-l pl-3"
            >
              <div className="text-sm font-medium">
                {event.title}
              </div>

              <div className="text-xs text-muted-foreground">
                {event.value ??
                  "-"}
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}