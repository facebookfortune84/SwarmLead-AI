"use client";

import { Input } from "@/components/ui/input";

interface Props {
  owner?: string | null;

  onChange: (
    owner: string
  ) => void;
}

export function LeadOwnerSelector({
  owner,
  onChange,
}: Props) {
  return (
    <Input
      value={owner ?? ""}
      placeholder="Assign owner"
      onChange={(e) =>
        onChange(
          e.target.value
        )
      }
    />
  );
}