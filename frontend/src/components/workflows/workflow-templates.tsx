"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Mail, Mic, Search, Zap, Repeat, ArrowRight, Loader2, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateWorkflowFromTemplate, useWorkflowTemplates } from "@/hooks/use-workflow-templates";

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  mail: Mail,
  mic: Mic,
  search: Search,
  zap: Zap,
  repeat: Repeat,
};

export function WorkflowTemplates() {
  const { data: templates = [], isLoading } = useWorkflowTemplates();
  const createTemplate = useCreateWorkflowFromTemplate();
  const [companyId, setCompanyId] = useState("");
  const [createdId, setCreatedId] = useState<string | null>(null);

  async function create(templateId: string, name: string) {
    if (!companyId.trim()) {
      alert("Enter a Tenant ID first (e.g. TEN-57253941).");
      return;
    }
    try {
      const result = await createTemplate.mutateAsync({ templateId, companyId: companyId.trim() });
      setCreatedId(result?.id ?? name);
      setTimeout(() => setCreatedId(null), 2500);
    } catch (err) {
      console.error("Failed to create workflow from template", err);
      alert("Failed to create workflow. Check the Tenant ID and try again.");
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-white/70 mb-1">
          Tenant ID
        </label>
        <Input
          value={companyId}
          onChange={(e) => setCompanyId(e.target.value)}
          placeholder="TEN-57253941"
          className="bg-white/5 border-white/10 text-white max-w-md"
        />
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-white/50">Loading templates...</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {templates.map((template, i) => {
            const Icon = ICON_MAP[template.icon] ?? Zap;
            return (
              <motion.div
                key={template.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="group relative bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-5 hover:border-indigo-500/30 transition-all duration-300 overflow-hidden"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shrink-0">
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="text-xs text-indigo-300/70 font-medium uppercase tracking-wide">
                      {template.category}
                    </div>
                    <h3 className="text-base font-semibold text-white leading-tight">
                      {template.name}
                    </h3>
                  </div>
                </div>

                <p className="text-sm text-white/60 mb-4 min-h-[40px]">
                  {template.description}
                </p>

                <div className="flex flex-wrap gap-1.5 mb-4">
                  {template.steps.slice(0, 3).map((step) => (
                    <span
                      key={step.step_name}
                      className="px-2 py-0.5 rounded-md bg-white/5 border border-white/[0.06] text-[11px] text-white/50"
                    >
                      {step.step_name}
                    </span>
                  ))}
                  {template.steps.length > 3 && (
                    <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/[0.06] text-[11px] text-white/40">
                      +{template.steps.length - 3} more
                    </span>
                  )}
                </div>

                <Button
                  onClick={() => create(template.id, template.name)}
                  disabled={createTemplate.isPending}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500"
                >
                  {createdId === template.name ? (
                    <>
                      <Check className="w-4 h-4 mr-2" /> Created
                    </>
                  ) : createTemplate.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Creating...
                    </>
                  ) : (
                    <>
                      Use Template <ArrowRight className="w-4 h-4 ml-1" />
                    </>
                  )}
                </Button>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
