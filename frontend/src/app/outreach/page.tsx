"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { OutreachForm } from "@/components/outreach/outreach-form";
import { CampaignForm } from "@/components/outreach/campaign-form";
import { CampaignTemplateGrid, CAMPAIGN_TEMPLATES, type CampaignTemplate } from "@/components/outreach/campaign-template-grid";
import { useLeads } from "@/hooks/use-leads";
import { useWorkflows } from "@/hooks/use-workflows";
import { Users, Megaphone, Workflow, Mic, Loader2, Target, Send } from "lucide-react";
import { motion } from "framer-motion";

export default function OutreachPage() {
  const [selectedTemplate, setSelectedTemplate] = useState<CampaignTemplate | null>(null);
  const { data: leads = [], isLoading: leadsLoading } = useLeads();
  const { data: workflows = [], isLoading: workflowsLoading } = useWorkflows();

  const qualifiedLeads = leads.filter((l: { status?: string }) => l.status === "QUALIFIED").length;
  const runningWorkflows = workflows.filter((w: { status?: string }) => w.status === "running").length;

  const stats = [
    { label: "Total Leads", value: leadsLoading ? "..." : leads.length.toString(), icon: Users, color: "text-blue-400" },
    { label: "Qualified", value: leadsLoading ? "..." : qualifiedLeads.toString(), icon: Target, color: "text-emerald-400" },
    { label: "Running Workflows", value: workflowsLoading ? "..." : runningWorkflows.toString(), icon: Workflow, color: "text-indigo-400" },
    { label: "Voice Agent", value: "Active", icon: Mic, color: "text-purple-400" },
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white">Outreach Center</h1>
          <p className="text-white/50 mt-1">Campaign execution, lead engagement, and AI-assisted prospecting</p>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
              >
                <Card className="p-4 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-white/50">{stat.label}</div>
                    <Icon className={`w-4 h-4 ${stat.color}`} />
                  </div>
                  <div className="mt-2 text-2xl font-bold text-white">{stat.value}</div>
                </Card>
              </motion.div>
            );
          })}
        </div>

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">Campaign Templates</h2>
            {selectedTemplate && (
              <button
                onClick={() => setSelectedTemplate(null)}
                className="text-xs text-white/40 hover:text-white/70 transition-colors"
              >
                Clear selection
              </button>
            )}
          </div>
          <CampaignTemplateGrid onSelect={(t) => setSelectedTemplate(t)} />
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <div className="flex items-center gap-2 mb-4">
              <Send className="w-4 h-4 text-indigo-400" />
              <h2 className="font-semibold text-white">Single Outreach</h2>
            </div>
            <OutreachForm />
          </Card>

          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <div className="flex items-center gap-2 mb-4">
              <Megaphone className="w-4 h-4 text-purple-400" />
              <h2 className="font-semibold text-white">Campaign Broadcast</h2>
            </div>
            <CampaignForm template={selectedTemplate} />
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
