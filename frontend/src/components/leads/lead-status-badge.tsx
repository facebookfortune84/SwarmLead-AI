import { Badge } from "@/components/ui/badge";

interface Props {
  status: string;
}

export function LeadStatusBadge({
  status,
}: Props) {
  const variant =
    status === "NEW"
      ? "default"
      : status === "CONTACTED"
      ? "secondary"
      : "outline";

  return (
    <Badge variant={variant}>
      {status}
    </Badge>
  );
}