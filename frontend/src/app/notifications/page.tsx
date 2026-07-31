"use client";

import { AppShell } from "@/components/layout/app-shell";
import { NotificationCenter } from "@/components/notifications/notification-center";
import { Bell } from "lucide-react";
import { motion } from "framer-motion";

export default function NotificationsPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-2">
            <Bell className="w-6 h-6 text-purple-400" />
            <h1 className="text-3xl font-bold text-white">Notifications</h1>
          </div>
          <p className="text-white/50 mt-1">Platform alerts, workflow status, outreach activity, and tenant events</p>
        </motion.div>

        <NotificationCenter />
      </div>
    </AppShell>
  );
}
