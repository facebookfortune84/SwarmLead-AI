"use client";

import {
  useLeadTimeline,
} from "@/hooks/use-lead-timeline";

interface Props {
  leadId: string;
}

export function LeadTimeline({
  leadId,
}: Props) {
  const {
    data,
    isLoading,
  } =
    useLeadTimeline(
      leadId
    );

  if (isLoading) {
    return (
      <div>
        Loading timeline...
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {(data ?? []).map(
        (
          item: unknown,
          index: number
        ) => (
          <div
            key={index}
            className="rounded-lg border p-3"
          >
            <pre className="text-xs">
              {JSON.stringify(
                item,
                null,
                2
              )}
            </pre>
          </div>
        )
      )}
    </div>
  );
}