"use client";

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

const STATUSES = [
  "NEW",
  "CONTACTED",
  "QUALIFIED",
  "MEETING",
  "PROPOSAL",
  "CUSTOMER",
  "LOST",
];

interface Props {
  value: string;
  onChange: (
    status: string
  ) => void;
}

export function LeadStatusMenu({
  value,
  onChange,
}: Props) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className="
          inline-flex
          h-9
          items-center
          rounded-md
          border
          px-3
          text-sm
        "
      >
        {value}
      </DropdownMenuTrigger>

      <DropdownMenuContent>
        {STATUSES.map(
          (status) => (
            <DropdownMenuItem
              key={status}
              onClick={() =>
                onChange(status)
              }
            >
              {status}
            </DropdownMenuItem>
          )
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}