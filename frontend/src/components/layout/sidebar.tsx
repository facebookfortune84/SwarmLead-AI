"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserMenu } from "./user-menu";

const items = [
  {
    href: "/dashboard",
    label: "Dashboard",
  },
  {
    href: "/leads",
    label: "Leads",
  },
  {
    href: "/tickets",
    label: "Tickets",
  },
  {
    href: "/workflows",
    label: "Workflows",
  },
  {
    href: "/tenants",
    label: "Tenants",
  },
  {
    href: "/outreach",
    label: "Outreach",
  },
  {
    href: "/settings",
    label: "Settings",
  },
];

export function Sidebar() {
  const pathname =
    usePathname();

  return (
    <aside className="flex w-64 flex-col border-r bg-background">
      <div className="border-b p-6">
        <div className="text-xl font-bold">
          SwarmLead AI
        </div>

        <div className="text-xs text-muted-foreground">
          CRM + Workflow Platform
        </div>
      </div>

      <nav className="flex-1 p-4">
        <div className="space-y-1">
          {items.map((item) => {
            const active = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm font-medium ${
                  active
                    ? "bg-muted text-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>

      <div className="border-t p-4">
        <UserMenu />
        <div className="mt-4 text xs text-muted-foreground">
          v0.6.x
        </div>
      </div>
    </aside>
  );
}