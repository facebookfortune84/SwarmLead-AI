"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSendCampaign } from "@/hooks/use-send-campaign";
import { Megaphone, Loader2, CheckCircle2, AlertCircle, Users, Wand2 } from "lucide-react";
import type { CampaignTemplate } from "./campaign-template-grid";

interface FormValues {
  recipients: string;
  subject: string;
  body: string;
  from_name: string;
}

interface CampaignFormProps {
  template?: CampaignTemplate | null;
}

export function CampaignForm({ template }: CampaignFormProps) {
  const campaign = useSendCampaign();
  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm<FormValues>();

  useEffect(() => {
    if (template) {
      setValue("subject", template.subject, { shouldValidate: true });
      setValue("body", template.body, { shouldValidate: true });
    }
  }, [template, setValue]);

  function parseRecipients(value: string): string[] {
    return value
      .split("\n")
      .map((v) => v.trim())
      .filter(Boolean);
  }

  async function submit(values: FormValues) {
    const recipients = parseRecipients(values.recipients);
    try {
      await campaign.mutateAsync({
        recipients,
        subject: values.subject,
        body: values.body,
        from_name: values.from_name || "SwarmOS",
      });
      reset();
    } catch {
      /* error surfaced below */
    }
  }

  const isPending = campaign.isPending;

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4">
      {template && (
        <div className="flex items-center gap-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 p-3 text-sm text-indigo-300">
          <Wand2 className="w-4 h-4 shrink-0" />
          Template <span className="font-medium">"{template.name}"</span> applied — edit the fields below or pick another template.
        </div>
      )}

      <div>
        <div className="flex items-center gap-2 mb-1">
          <Users className="w-3.5 h-3.5 text-white/40" />
          <span className="text-xs text-white/50">Recipients (one per line)</span>
        </div>
        <textarea
          className="min-h-[150px] w-full rounded-xl border border-white/10 bg-white/5 p-4 text-white placeholder:text-white/30 focus:outline-none focus:border-indigo-500/50"
          placeholder="one@example.com&#10;two@example.com"
          {...register("recipients", {
            validate: (value) => {
              const parsed = parseRecipients(value);
              if (parsed.length === 0) return "Add at least one recipient email";
              const invalid = parsed.filter((e) => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e));
              if (invalid.length > 0) return `Invalid email: ${invalid[0]}`;
              return true;
            },
          })}
        />
        {errors.recipients && <p className="mt-1 text-xs text-red-400">{errors.recipients.message}</p>}
      </div>

      <div>
        <Input
          placeholder="Campaign Subject"
          className="bg-white/5 border-white/10 text-white placeholder:text-white/30"
          {...register("subject", { required: "Subject is required" })}
        />
        {errors.subject && <p className="mt-1 text-xs text-red-400">{errors.subject.message}</p>}
      </div>

      <div>
        <Input
          placeholder="Sender Name (optional, defaults to SwarmOS)"
          className="bg-white/5 border-white/10 text-white placeholder:text-white/30"
          {...register("from_name")}
        />
      </div>

      <div>
        <textarea
          className="min-h-[250px] w-full rounded-xl border border-white/10 bg-white/5 p-4 text-white placeholder:text-white/30 focus:outline-none focus:border-indigo-500/50"
          placeholder="Campaign Body"
          {...register("body", { required: "Campaign body is required", minLength: { value: 10, message: "Body should be at least 10 characters" } })}
        />
        {errors.body && <p className="mt-1 text-xs text-red-400">{errors.body.message}</p>}
      </div>

      {campaign.isError && (
        <div className="flex items-start gap-2 rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-300">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>
            {campaign.error instanceof Error
              ? (campaign.error as any).response?.data?.detail?.error
                ?? (campaign.error as any).response?.data?.detail
                ?? campaign.error.message
              : "Failed to launch campaign. Please try again."}
          </span>
        </div>
      )}

      {campaign.isSuccess && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3 text-sm text-emerald-300">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          Campaign queued — {(campaign.data as any)?.queued ?? "messages"} enqueued.
        </div>
      )}

      <Button type="submit" disabled={isPending} className="w-full">
        {isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Megaphone className="w-4 h-4 mr-2" />}
        {isPending ? "Launching..." : "Launch Campaign"}
      </Button>
    </form>
  );
}
