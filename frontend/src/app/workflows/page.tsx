"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { WorkflowCreateForm } from "@/components/workflows/workflow-create-form";
import { WorkflowHistoryList } from "@/components/workflows/workflow-history-list";
import { WorkflowOverviewCard } from "@/components/workflows/workflow-overview-card";
import { Workflow, ListOrdered } from "lucide-react";
import { motion } from "framer-motion";

export default function WorkflowsPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white">Workflow Center</h1>
          <p className="text-white/50 mt-1">Automation runtime, orchestration, execution, and workflow operations</p>
        </motion.div>

        <WorkflowOverviewCard />

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <div className="flex items-center gap-2 mb-4">
            <Workflow className="w-4 h-4 text-indigo-400" />
            <h2 className="font-semibold text-white">Create Workflow</h2>
          </div>
          <WorkflowCreateForm />
        </Card>

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <div className="flex items-center gap-2 mb-4">
            <ListOrdered className="w-4 h-4 text-purple-400" />
            <h2 className="font-semibold text-white">Workflow History</h2>
          </div>
          <WorkflowHistoryList />
        </Card>
      </div>
    </AppShell>
  );
}
