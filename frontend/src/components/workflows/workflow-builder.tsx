"use client";

import { useState } from "react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Step {
  step_name: string;
  step_type: string;
}

export function WorkflowBuilder() {
  const [name, setName] =
    useState("");

  const [steps, setSteps] =
    useState<Step[]>([
      {
        step_name:
          "Qualification",
        step_type:
          "notification",
      },
    ]);

  function addStep() {
    setSteps((current) => [
      ...current,
      {
        step_name: "",
        step_type:
          "notification",
      },
    ]);
  }

  return (
    <Card className="p-6">
      <h2 className="font-semibold">
        Workflow Builder
      </h2>

      <div className="mt-4 space-y-4">
        <Input
          placeholder="Workflow Name"
          value={name}
          onChange={(e) =>
            setName(
              e.target.value
            )
          }
        />

        {steps.map(
          (step, index) => (
            <Input
              key={index}
              value={
                step.step_name
              }
              placeholder={`Step ${index + 1}`}
              onChange={(
                e
              ) => {
                const copy =
                  [...steps];

                copy[
                  index
                ].step_name =
                  e.target.value;

                setSteps(
                  copy
                );
              }}
            />
          )
        )}

        <Button
          variant="outline"
          onClick={addStep}
        >
          Add Step
        </Button>
      </div>
    </Card>
  );
}