"use client";

import { createElement, useState } from "react";

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

import { Button } from "@/components/ui/button";

import { useWorkflows } from "@/hooks/use-workflows";

interface Props {
  leadId: string;
}

interface Workflow {
  id: string;
  name: string;
}

export function WorkflowLauncher({
  leadId,
}: Props) {
  const { data = [] } =
    useWorkflows();

  const [
    launching,
    setLaunching,
  ] = useState(false);

  async function launch(
    workflowId: string
  ) {
    try {
      setLaunching(true);

      console.log(
        "Launch workflow",
        workflowId,
        leadId
      );
    } finally {
      setLaunching(false);
    }
  }

  return createElement(
    DropdownMenu,
    null,
    createElement(
      DropdownMenuTrigger,
      {
        className:
          "inline-flex items-center rounded-md border px-3 py-2 text-sm",
      },
      launching ? "Launching..." : "Run Workflow"
    ),
    createElement(
      DropdownMenuContent,
      null,
      ...data.map((workflow: Workflow) =>
        createElement(
          DropdownMenuItem,
          {
            key: workflow.id,
            onClick: () => launch(workflow.id),
          },
          workflow.name
        )
      )
    )
  );
}