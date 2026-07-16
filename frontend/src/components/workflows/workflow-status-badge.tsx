"use client";

interface Props {
  status: string;
}

export function WorkflowStatusBadge({
  status,
}: Props) {
  const color =
    {
      pending:
        "bg-yellow-100 text-yellow-700",

      running:
        "bg-blue-100 text-blue-700",

      paused:
        "bg-orange-100 text-orange-700",

      completed:
        "bg-green-100 text-green-700",

      failed:
        "bg-red-100 text-red-700",
    }[
      status
    ] ??
    "bg-muted";

  return (
    <span
      className={`rounded px-3 py-1 text-xs font-medium ${color}`}
    >
      {status}
    </span>
  );
}