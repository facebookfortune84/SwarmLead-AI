"use client";

import Link from "next/link";
import { useWorkflows } from "@/hooks/use-workflows";
import { Loader2, XCircle, Inbox, ChevronRight, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";
import { WorkflowStatusBadge } from "./workflow-status-badge";

type Workflow = {
  id: string;
  name: string;
  status?: string;
};

export function WorkflowHistoryList() {
  const { data = [], isLoading, isError, refetch } = useWorkflows();

  const workflows: Workflow[] = data as Workflow[];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12 text-white/40">
        <Loader2 className="w-5 h-5 text-indigo-400 animate-spin mr-2" />
        Loading workflows...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-12 rounded-xl bg-red-500/10 border border-red-500/20">
        <XCircle className="w-8 h-8 text-red-400 mb-3" />
        <p className="text-sm font-medium text-red-300">Failed to load workflows</p>
        <p className="text-xs text-white/40 mt-1 mb-4">The workflow API could not be reached.</p>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/20 text-red-300 text-sm hover:bg-red-500/30 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Retry
        </button>
      </div>
    );
  }

  if (workflows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 rounded-xl bg-white/5 border border-white/[0.06]">
        <Inbox className="w-8 h-8 text-white/20 mb-3" />
        <p className="text-sm font-medium text-white/60">No workflows yet</p>
        <p className="text-xs text-white/40 mt-1">Create your first workflow above to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {workflows.map((workflow, i) => (
        <motion.div
          key={workflow.id}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
        >
          <Link
            href={`/workflows/${workflow.id}`}
            className="group block rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 hover:border-indigo-500/30 hover:bg-white/[0.04] transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="font-medium text-white">{workflow.name}</div>
              <div className="flex items-center gap-3">
                {workflow.status && <WorkflowStatusBadge status={workflow.status} />}
                <ChevronRight className="w-4 h-4 text-white/20 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
              </div>
            </div>
          </Link>
        </motion.div>
      ))}
    </div>
  );
}
