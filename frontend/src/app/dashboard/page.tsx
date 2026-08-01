"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CompanyBuilder } from "@/components/company/company-builder";
import { useDashboard } from "@/hooks/use-dashboard";
import { useNotifications } from "@/hooks/use-notifications";
import { useWorkflows } from "@/hooks/use-workflows";
import { WorkflowStatusBadge } from "@/components/workflows/workflow-status-badge";
import {
  Users, Target, Briefcase, Building2, Activity, Workflow as WorkflowIcon,
  Bell, Loader2, ArrowRight, Server, Shield, Mic, CheckCircle2,
} from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function DashboardPage() {
  const { data, isLoading, isError } = useDashboard();
  const { data: notifications, isLoading: notificationsLoading } = useNotifications({ limit: 5 });
  const { data: workflows = [], isLoading: workflowsLoading } = useWorkflows();

  const notifItems = notifications?.items ?? [];
  const workflowItems = workflows.slice(0, 5) as { id: string; name: string; status?: string }[];

  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-white/50 mt-1">Lead intelligence, workflows, outreach, voice agents, and tenant operations</p>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            { label: "Total Leads", value: data?.leads, icon: Users, color: "text-blue-400" },
            { label: "Qualified Leads", value: data?.qualifiedLeads, icon: Target, color: "text-emerald-400" },
            { label: "Customers", value: data?.customers, icon: Briefcase, color: "text-purple-400" },
            { label: "Tenants", value: data?.tenants, icon: Building2, color: "text-amber-400" },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
              >
                <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm text-white/50">{stat.label}</h3>
                    <Icon className={`w-4 h-4 ${stat.color}`} />
                  </div>
                  <p className="mt-2 text-3xl font-bold text-white">
                    {isLoading ? <Loader2 className="w-6 h-6 text-white/30 animate-spin inline" /> : (stat.value ?? 0)}
                  </p>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {isError && (
          <Card className="p-4 bg-white/[0.03] backdrop-blur-xl border-red-500/20">
            <div className="text-sm text-red-300">
              Some dashboard data could not be loaded. Recent activity may be missing.
            </div>
          </Card>
        )}

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <div className="flex items-center gap-2 mb-4">
            <Building2 className="w-4 h-4 text-emerald-400" />
            <h2 className="font-semibold text-white">Company Builder</h2>
            <span className="ml-2 text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300">
              Agent Swarm
            </span>
          </div>
          <p className="text-sm text-white/50 mb-5">
            Describe a business and Genesis will run its strategy, content, SEO, and growth agents to
            produce a complete, downloadable company package.
          </p>
          <CompanyBuilder />
        </Card>

        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <WorkflowIcon className="w-4 h-4 text-indigo-400" />
                <h2 className="font-semibold text-white">Workflow Center</h2>
              </div>
              <Link href="/workflows" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                View all <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {workflowsLoading ? (
              <div className="mt-4 flex items-center justify-center py-8 text-white/40">
                <Loader2 className="w-4 h-4 text-indigo-400 animate-spin mr-2" /> Loading workflows...
              </div>
            ) : workflowItems.length === 0 ? (
              <div className="mt-4 rounded-xl bg-white/5 border border-white/[0.06] py-8 text-center text-sm text-white/40">
                No workflows yet. Create one in the Workflow Center.
              </div>
            ) : (
              <ul className="mt-4 space-y-3 text-sm">
                {workflowItems.map((wf, i) => (
                  <motion.li
                    key={wf.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"
                  >
                    <Link href={`/workflows/${wf.id}`} className="text-white hover:text-indigo-300 transition-colors">
                      {wf.name}
                    </Link>
                    {wf.status && <WorkflowStatusBadge status={wf.status} />}
                  </motion.li>
                ))}
              </ul>
            )}
          </Card>

          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bell className="w-4 h-4 text-purple-400" />
                <h2 className="font-semibold text-white">Recent Notifications</h2>
              </div>
              <Link href="/notifications" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                View all <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {notificationsLoading ? (
              <div className="mt-4 flex items-center justify-center py-8 text-white/40">
                <Loader2 className="w-4 h-4 text-indigo-400 animate-spin mr-2" /> Loading...
              </div>
            ) : notifItems.length === 0 ? (
              <div className="mt-4 rounded-xl bg-white/5 border border-white/[0.06] py-8 text-center text-sm text-white/40">
                No notifications yet.
              </div>
            ) : (
              <ul className="mt-4 space-y-3 text-sm">
                {notifItems.map((n, i) => (
                  <motion.li
                    key={n.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-white">{n.title}</span>
                      <span className="text-xs text-white/30">{formatDate(n.created_at)}</span>
                    </div>
                    <p className="mt-1 text-xs text-white/50 line-clamp-2">{n.message}</p>
                  </motion.li>
                ))}
              </ul>
            )}
          </Card>
        </div>

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <h2 className="font-semibold text-white">Platform Status</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-4">
            {[
              { label: "CRM", icon: Server, status: "Online", color: "text-emerald-400" },
              { label: "API", icon: Shield, status: "Online", color: "text-emerald-400" },
              { label: "Workflows", icon: WorkflowIcon, status: `${data?.runningWorkflows ?? 0} running`, color: "text-indigo-400" },
              { label: "Voice", icon: Mic, status: "Active", color: "text-purple-400" },
            ].map((item, i) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="rounded-xl bg-white/5 p-4"
                >
                  <div className="flex items-center gap-2">
                    <Icon className={`w-4 h-4 ${item.color}`} />
                    <div className="text-sm text-white/50">{item.label}</div>
                  </div>
                  <div className={`mt-2 flex items-center gap-1.5 font-semibold ${item.color}`}>
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {item.status}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
