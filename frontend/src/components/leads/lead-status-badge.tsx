import { Badge } from "@/components/ui/badge";

interface Props {
  status: string;
}

const STATUS_STYLES: Record<
  string,
  string
> = {
  NEW: "bg-blue-500 text-white",

  CONTACTED:
    "bg-amber-500 text-white",

  QUALIFIED:
    "bg-purple-500 text-white",

  MEETING:
    "bg-cyan-500 text-white",

  PROPOSAL:
    "bg-orange-500 text-white",

  CUSTOMER:
    "bg-green-600 text-white",

  LOST: "bg-red-600 text-white",
};

export function LeadStatusBadge({
  status,
}: Props) {
  return (
    <Badge
      className={
        STATUS_STYLES[
          status
        ] ??
        "bg-secondary"
      }
    >
      {status}
    </Badge>
  );
}