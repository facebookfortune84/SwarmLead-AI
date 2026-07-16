"use client";

import {
  useForm,
} from "react-hook-form";

import { Button } from "@/components/ui/button";

import { Input } from "@/components/ui/input";

import {
  useSendCampaign,
} from "@/hooks/use-send-campaign";

interface FormValues {
  recipients: string;

  subject: string;

  body: string;

  from_name: string;
}

export function CampaignForm() {
  const campaign =
    useSendCampaign();

  const {
    register,
    handleSubmit,
    reset,
  } =
    useForm<FormValues>();

  async function submit(
    values: FormValues
  ) {
    await campaign.mutateAsync(
      {
        recipients:
          values.recipients
            .split("\n")
            .map((v) =>
              v.trim()
            )
            .filter(
              Boolean
            ),

        subject:
          values.subject,

        body:
          values.body,

        from_name:
          values.from_name,
      }
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
      <textarea
        className="min-h-[150px] w-full rounded border p-4"
        placeholder="One email address per line"
        {...register(
          "recipients"
        )}
      />

      <Input
        placeholder="Campaign Subject"
        {...register(
          "subject"
        )}
      />

      <Input
        placeholder="Sender Name"
        {...register(
          "from_name"
        )}
      />

      <textarea
        className="min-h-[250px] w-full rounded border p-4"
        placeholder="Campaign Body"
        {...register(
          "body"
        )}
      />

      <Button
        type="submit"
      >
        Launch Campaign
      </Button>
    </form>
  );
}