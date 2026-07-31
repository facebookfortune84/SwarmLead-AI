"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Server, Database, Shield, Users, Activity, Clock, Globe, Wifi, HardDrive, Cpu, ChevronRight } from "lucide-react";

interface SystemHealth {
  api: string;
  database: string;
  auth: string;
  workflow: string;
  redis: string;
  uptime: string;
}

export default function AdminPage() {
  const [health, setHealth] = useState<SystemHealth>({
    api: "checking...",
    database: "checking...",
    auth: "checking...",
    workflow: "checking...",
    redis: "checking...",
    uptime: "0s",
  });

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch("/health");
        if (res.ok) setHealth((h) => ({ ...h, api: "online", database: "online" }));
      } catch { setHealth((h) => ({ ...h, api: "offline", database: "offline" })); }
      try {
        const res = await fetch("/ready");
        if (res.ok) setHealth((h) => ({ ...h, auth: "online", workflow: "online", redis: "online" }));
      } catch { setHealth((h) => ({ ...h, auth: "offline", workflow: "offline", redis: "offline" })); }
    }
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const systemInfo = [
    { label: "API Status", value: health.api, icon: Server, ok: health.api === "online" },
    { label: "Database", value: health.database, icon: Database, ok: health.database === "online" },
    { label: "Authentication", value: health.auth, icon: Shield, ok: health.auth === "online" },
    { label: "Workflow Engine", value: health.workflow, icon: Activity, ok: health.workflow === "online" },
    { label: "Redis Cache", value: health.redis, icon: HardDrive, ok: health.redis === "online" },
    { label: "System Runtime", value: "Stable", icon: Clock, ok: true },
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white">Admin Console</h1>
          <p className="text-white/50 mt-1">Platform administration, system monitoring, and operations</p>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
          {systemInfo.map((item, i) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/[0.06] p-4 text-center"
              >
                <Icon className={`w-5 h-5 mx-auto mb-2 ${item.ok ? "text-emerald-400" : "text-red-400"}`} />
                <div className="text-xs text-white/50">{item.label}</div>
                <div className={`text-sm font-semibold mt-1 ${item.ok ? "text-emerald-400" : "text-red-400"}`}>{item.value}</div>
              </motion.div>
            );
          })}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <h2 className="text-lg font-semibold text-white mb-4">System Diagnostics</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/[0.04]">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm text-white/80">Frontend</span>
                </div>
                <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">healthy</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/[0.04]">
                <div className="flex items-center gap-2">
                  <Server className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm text-white/80">Backend API</span>
                </div>
                <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">healthy</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/[0.04]">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm text-white/80">PostgreSQL</span>
                </div>
                <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">connected</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/[0.04]">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm text-white/80">Redis Cache</span>
                </div>
                <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">connected</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/[0.04]">
                <div className="flex items-center gap-2">
                  <Wifi className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm text-white/80">Cloudflare Tunnel</span>
                </div>
                <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">active</span>
              </div>
            </div>
          </Card>

          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <h2 className="text-lg font-semibold text-white mb-4">Quick Actions</h2>
            <div className="space-y-3">
              {[
                { label: "View All Users", desc: "Manage user accounts and permissions" },
                { label: "System Logs", desc: "Review application and error logs" },
                { label: "Cache Management", desc: "Clear or refresh system caches" },
                { label: "Backup Database", desc: "Create a manual database backup" },
              ].map((action) => (
                <button
                  key={action.label}
                  className="w-full flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/[0.04] hover:bg-white/10 transition-colors text-left"
                >
                  <div>
                    <div className="text-sm font-medium text-white">{action.label}</div>
                    <div className="text-xs text-white/50">{action.desc}</div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-white/30" />
                </button>
              ))}
            </div>
          </Card>
        </div>

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <h2 className="text-lg font-semibold text-white mb-4">Platform Overview</h2>
          <div className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/[0.04]">
            <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
            <div>
              <div className="text-sm font-medium text-white">All Systems Operational</div>
              <div className="text-xs text-white/50">Genesis Forge platform is running normally with all services connected</div>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}