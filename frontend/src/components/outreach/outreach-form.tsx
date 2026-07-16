"use client";

import {
  useForm,
} from "react-hook-form";

import { Input } from "@/components/ui/input";

import { Button } from "@/components/ui/button";

import {
  useSendOutreach,
} from "@/hooks/use-send-outreach";

interface FormValues {
  email: string;
  subject: string;
  body: string;
}

export function OutreachForm() {
  const outreach =
    useSendOutreach();

  const {
    register,
    handleSubmit,
    reset,
  } =
    useForm<FormValues>();

  async function submit(
    data: FormValues
  ) {
    await outreach.mutateAsync(
      data
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
        placeholder="Recipient Email"
        {...register(
          "email",
          {
            required:
              true,
          }
        )}
      />

      <Input
        placeholder="Subject"
        {...register(
          "subject",
          {
            required:
              true,
          }
        )}
      />

      <textarea
        className="min-h-[200px] w-full rounded-md border p-4"
        placeholder="Message"
        {...register(
          "body",
          {
            required:
              true,
          }
        )}
      />

      <Button
        type="submit"
      >
        Send Outreach
      </Button>
    </form>
  );
}