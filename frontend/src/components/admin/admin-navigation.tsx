"use client";

import Link from "next/link";

export function AdminNavigation() {
  return (
    <div className="rounded-lg border p-4">
      <div className="font-medium">
        Administration
      </div>

      <div className="mt-4 flex flex-wrap gap-4">
        <Link href="/admin" className="rounded-lg border px-3 py-2 text-sm font-medium hover:bg-slate-50">
          Dashboard
        </Link>

        <Link href="/admin/users" className="rounded-lg border px-3 py-2 text-sm font-medium hover:bg-slate-50">
          Users
        </Link>

        <Link href="/notifications" className="rounded-lg border px-3 py-2 text-sm font-medium hover:bg-slate-50">
          Notifications
        </Link>

        <Link href="/workflows" className="rounded-lg border px-3 py-2 text-sm font-medium hover:bg-slate-50">
          Workflows
        </Link>
      </div>
    </div>
  );
}