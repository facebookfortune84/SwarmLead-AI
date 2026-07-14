"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import { useWorkflows } from "@/hooks/use-workflows";

import {
  useStartWorkflow,
  usePauseWorkflow,
  useResumeWorkflow,
} from "@/hooks/use-run-workflow";

type Workflow = {
  id: string;
  name: string;
  status: string;
};

export default function WorkflowsPage() {
  const {
    data = [],
    isLoading,
    error,
  } = useWorkflows();

  const startWorkflow =
    useStartWorkflow();

  const pauseWorkflow =
    usePauseWorkflow();

  const resumeWorkflow =
    useResumeWorkflow();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Workflow Center
        </h1>

        <p className="text-muted-foreground">
          Automation engine, agent orchestration,
          outreach execution, and future voice routing.
        </p>
      </div>

      {error ? (
        <Card className="p-6">
          <div className="font-medium">
            Authentication Required
          </div>

          <div className="mt-2 text-sm text-muted-foreground">
            Login is required before workflows
            can be viewed or executed.
          </div>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="p-6">
          Loading workflows...
        </Card>
      ) : (
        <div className="space-y-4">
          {data.length === 0 ? (
            <Card className="p-6">
              <div className="font-medium">
                No workflows found
              </div>

              <div className="mt-2 text-sm text-muted-foreground">
                Create a workflow to begin
                automation.
              </div>
            </Card>
          ) : (
            data.map((workflow: Workflow) => (
                <Card
                  key={
                    workflow.id
                  }
                  className="p-6"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="font-semibold">
                        {
                          workflow.name
                        }
                      </h2>

                      <div className="mt-1 text-sm text-muted-foreground">
                        Status:{" "}
                        {
                          workflow.status
                        }
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() =>
                          startWorkflow.mutate(
                            workflow.id
                          )
                        }
                      >
                        Start
                      </Button>

                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          pauseWorkflow.mutate(
                            workflow.id
                          )
                        }
                      >
                        Pause
                      </Button>

                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          resumeWorkflow.mutate(
                            workflow.id
                          )
                        }
                      >
                        Resume
                      </Button>
                    </div>
                  </div>
                </Card>
              )
            )
          )}
        </div>
      )}
    </div>
  );
}