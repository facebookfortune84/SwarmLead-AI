"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export interface WorkflowTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  icon: string;
  steps: { step_name: string; step_type: string }[];
}

export function useWorkflowTemplates() {
  return useQuery({
    queryKey: ["workflow-templates"],
    queryFn: async () => {
      const response = await api.get("/api/workflows/templates");
      return response.data.templates as WorkflowTemplate[];
    },
  });
}

export function useCreateWorkflowFromTemplate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      templateId,
      companyId,
    }: {
      templateId: string;
      companyId: string;
    }) => {
      const response = await api.post("/api/workflows/from-template", {
        template_id: templateId,
        company_id: companyId,
      });
      return response.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}
