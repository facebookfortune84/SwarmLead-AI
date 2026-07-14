"use client";

import { Badge } from "@/components/ui/badge";

interface Props {
  status: string;
}

const COLORS: Record<
  string,
  string
> = {
  pending:
    "bg-zinc-500 text-white",

  running:
    "bg-green-600 text-white",

  paused:
    "bg-yellow-500 text-white",

  completed:
    "bg-blue-600 text-white",

  failed:
    "bg-red-600 text-white",
};

export function WorkflowStatusBadge({
  status,
}: Props) {
  return (
    <Badge
      className={
        COLORS[status] ??
        "bg-secondary"
      }
    >
      {status}
    </Badge>
  );
}