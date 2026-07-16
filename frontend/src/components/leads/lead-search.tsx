"use client";

import { Input } from "@/components/ui/input";

interface Props {
  value: string;

  onChange: (
    value: string
  ) => void;
}

export function LeadSearch({
  value,
  onChange,
}: Props) {
  return (
    <Input
      placeholder="Search Leads"
      value={value}
      onChange={(e) =>
        onChange(
          e.target.value
        )
      }
    />
  );
}