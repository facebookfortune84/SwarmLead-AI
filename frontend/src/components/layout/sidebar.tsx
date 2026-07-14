"use client";

import Link from "next/link";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/leads", label: "Leads" },
  { href: "/tickets", label: "Tickets" },
  { href: "/workflows", label: "Workflows" },
  { href: "/tenants", label: "Tenants" },
  { href: "/outreach", label: "Outreach" },
  { href: "/settings", label: "Settings" },
];

export function Sidebar() {
  return (
    <aside className="w-64 border-r p-4">
      <div className="mb-6 text-xl font-bold">
        SwarmLead-AI
      </div>

      <nav className="space-y-2">
        {items.map((item) => (
          <Link key={item.href} href={item.href} className="block rounded px-3 py-2 text-sm font-medium hover:bg-gray-100">
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}