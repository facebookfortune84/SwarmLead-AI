"use client";

import {
  useForm,
} from "react-hook-form";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

import {
  useRegisterTenant,
} from "@/hooks/use-register-tenant";

interface FormValues {
  name: string;

  slug: string;
}

export function CreateTenantForm() {
  const registerTenant =
    useRegisterTenant();

  const {
    register,
    handleSubmit,
    reset,
  } =
    useForm<FormValues>();

  async function submit(
    values: FormValues
  ) {
    await registerTenant.mutateAsync(
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
        placeholder="Tenant Name"
        {...register(
          "name"
        )}
      />

      <Input
        placeholder="Tenant Slug"
        {...register(
          "slug"
        )}
      />

      <Button
        type="submit"
      >
        Create Tenant
      </Button>
    </form>
  );
}