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
    href: "/agents",
    label: "Agents",
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
    href: "/autonomy",
    label: "Autonomy",
  },
  {
    href: "/billing",
    label: "Billing",
  },
  {
    href: "/notifications",
    label: "Notifications",
  },
  {
    href: "/admin",
    label: "Admin",
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
        <h1 className="text-xl font-bold">
          <Link href="/" className="flex items-center gap-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/voice_agent_image_1.png"
              alt="Genesis Forge"
              className="h-8 w-8 rounded-full object-cover ring-1 ring-border"
            />
            <span className="flex flex-col leading-tight">
              <span>Genesis Forge</span>
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                by Realms 2 Riches
              </span>
            </span>
          </Link>
        </h1>

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