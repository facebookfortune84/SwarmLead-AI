"use client";

import { Lead } from "@/types/lead";

interface Props {
  leads: Lead[];
}

export function LeadMetrics({
  leads,
}: Props) {
  const total =
    leads.length;

  const newLeads =
    leads.filter(
      (l) =>
        l.status === "NEW"
    ).length;

  const qualified =
    leads.filter(
      (l) =>
        l.status ===
        "QUALIFIED"
    ).length;

  const customers =
    leads.filter(
      (l) =>
        l.status ===
        "CUSTOMER"
    ).length;

  const cards = [
    {
      label:
        "Total Leads",
      value: total,
    },
    {
      label:
        "New Leads",
      value: newLeads,
    },
    {
      label:
        "Qualified",
      value: qualified,
    },
    {
      label:
        "Customers",
      value: customers,
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-xl border p-4"
        >
          <div className="text-sm text-muted-foreground">
            {card.label}
          </div>

          <div className="mt-2 text-3xl font-bold">
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}