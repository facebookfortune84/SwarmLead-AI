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

  company_id: string;

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
    formState: { errors },
  } =
    useForm<FormValues>({
      defaultValues: {
        name: "",

        company_id: "",

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
    const name =
      values.name.trim();

    const companyId =
      values.company_id.trim();

    if (!name) {
      alert(
        "Workflow name is required."
      );
      return;
    }

    if (!companyId) {
      alert(
        "Tenant ID is required."
      );
      return;
    }

    try {
      // attach tenant id to each step's `input` to match createWorkflow's expected shape
      const stepsWithInput = values.steps.map((s) => ({
        ...s,
        input: { company_id: companyId },
      }));

      await createWorkflow.mutateAsync({
        name,
        steps: stepsWithInput,
      });

      reset({
        name: "",
        company_id: "",
        steps: [
          {
            step_name:
              "Start",
            step_type:
              "notification",
          },
        ],
      });
    } catch (error) {
      console.error(
        "Failed to create workflow",
        error
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(
        submit
      )}
      className="space-y-4"
    >
      <div>
        <Input
          placeholder="Workflow Name"
          {...register(
            "name",
            {
              required: true,
            }
          )}
        />

        {errors.name && (
          <p className="mt-1 text-sm text-red-500">
            Workflow name is
            required
          </p>
        )}
      </div>

      <div>
        <Input
          placeholder="Tenant ID (example: TEN-57253941)"
          {...register(
            "company_id",
            {
              required: true,
            }
          )}
        />

        {errors.company_id && (
          <p className="mt-1 text-sm text-red-500">
            Tenant ID is
            required
          </p>
        )}
      </div>

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
        disabled={
          createWorkflow.isPending
        }
      >
        {createWorkflow.isPending
          ? "Creating Workflow..."
          : "Create Workflow"}
      </Button>
    </form>
  );
}