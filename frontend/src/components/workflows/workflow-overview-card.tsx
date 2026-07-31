"use client";

import { Card } from "@/components/ui/card";
import { useWorkflows } from "@/hooks/use-workflows";
import { Activity, CheckCircle2, XCircle, Loader2, RefreshCw, Inbox } from "lucide-react";
import { motion } from "framer-motion";

interface WorkflowRuntime {
  id: string;
  name: string;
  status: string;
}

export function WorkflowOverviewCard() {
  const { data = [], isLoading, isError, refetch } = useWorkflows();

  const workflows = data as WorkflowRuntime[];

  const running = workflows.filter((w) => w.status === "running").length;
  const completed = workflows.filter((w) => w.status === "completed").length;
  const failed = workflows.filter((w) => w.status === "failed").length;
  const paused = workflows.filter((w) => w.status === "paused").length;
  const pending = workflows.filter((w) => w.status === "pending").length;

  if (isLoading) {
    return (
      <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-white">Workflow Metrics</h2>
          <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
        </div>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="animate-pulse rounded-xl bg-white/5 p-4">
              <div className="h-3 w-16 bg-white/10 rounded mb-2" />
              <div className="h-8 w-10 bg-white/10 rounded" />
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-white">Workflow Metrics</h2>
          <XCircle className="w-4 h-4 text-red-400" />
        </div>
        <div className="mt-4 flex items-center justify-between rounded-xl bg-red-500/10 border border-red-500/20 p-4">
          <div>
            <p className="text-sm font-medium text-red-300">Unable to load workflow metrics</p>
            <p className="text-xs text-white/40 mt-1">The API could not be reached. Check your connection.</p>
          </div>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/20 text-red-300 text-sm hover:bg-red-500/30 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </button>
        </div>
      </Card>
    );
  }

  const metrics = [
    { label: "Running", value: running, icon: Activity, color: "text-blue-400" },
    { label: "Pending", value: pending, icon: Inbox, color: "text-yellow-400" },
    { label: "Paused", value: paused, icon: RefreshCw, color: "text-orange-400" },
    { label: "Completed", value: completed, icon: CheckCircle2, color: "text-emerald-400" },
    { label: "Failed", value: failed, icon: XCircle, color: "text-red-400" },
  ];

  return (
    <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
      <h2 className="font-semibold text-white">Workflow Metrics</h2>
      <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
        {metrics.map((metric, i) => {
          const Icon = metric.icon;
          return (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="rounded-xl bg-white/5 p-4"
            >
              <div className="flex items-center justify-between">
                <div className="text-xs text-white/50">{metric.label}</div>
                <Icon className={`w-4 h-4 ${metric.color}`} />
              </div>
              <div className={`mt-2 text-2xl font-bold ${metric.color}`}>{metric.value}</div>
            </motion.div>
          );
        })}
      </div>
    </Card>
  );
}
