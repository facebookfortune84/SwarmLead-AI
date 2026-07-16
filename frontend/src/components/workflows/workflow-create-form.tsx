"use client";

import {
  useFieldArray,
  useForm,
} from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import {
  useCreateWorkflow,
} from "@/hooks/use-create-workflow";

interface FormValues {
  name: string;

  steps: {
    step_name: string;
    step_type: string;
  }[];
}

export function WorkflowCreateForm() {
  const createWorkflow =
    useCreateWorkflow();

  const {
    register,
    control,
    handleSubmit,
    reset,
  } =
    useForm<FormValues>({
      defaultValues: {
        name: "",

        steps: [
          {
            step_name:
              "Start",

            step_type:
              "notification",
          },
        ],
      },
    });

  const {
    fields,
    append,
    remove,
  } =
    useFieldArray({
      control,
      name: "steps",
    });

  async function submit(
    values: FormValues
  ) {
    await createWorkflow.mutateAsync(
      values
    );

    reset();
  }

  return (
    <form
      onSubmit={handleSubmit(
        submit
      )}
      className="space-y-4"
    >
      <Input
        placeholder="Workflow Name"
        {...register(
          "name"
        )}
      />

      {fields.map(
        (
          field,
          index
        ) => (
          <div
            key={
              field.id
            }
            className="grid gap-2 md:grid-cols-3"
          >
            <Input
              placeholder="Step Name"
              {...register(
                `steps.${index}.step_name`
              )}
            />

            <Input
              placeholder="Step Type"
              {...register(
                `steps.${index}.step_type`
              )}
            />

            <Button
              type="button"
              variant="outline"
              onClick={() =>
                remove(
                  index
                )
              }
            >
              Remove
            </Button>
          </div>
        )
      )}

      <Button
        type="button"
        variant="outline"
        onClick={() =>
          append({
            step_name: "",
            step_type:
              "notification",
          })
        }
      >
        Add Step
      </Button>

      <Button
        type="submit"
      >
        Create Workflow
      </Button>
    </form>
  );
}