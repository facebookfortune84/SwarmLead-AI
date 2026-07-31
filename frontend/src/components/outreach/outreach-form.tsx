"use client";

import { useForm } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useSendOutreach } from "@/hooks/use-send-outreach";
import { CheckCircle2, Loader2, Send, AlertCircle } from "lucide-react";

interface FormValues {
  email: string;
  subject: string;
  body: string;
}

export function OutreachForm() {
  const outreach = useSendOutreach();
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>();

  async function submit(data: FormValues) {
    try {
      await outreach.mutateAsync(data);
      reset();
    } catch {
      /* error surfaced below */
    }
  }

  const isPending = outreach.isPending;

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4">
      <div>
        <Input
          placeholder="Recipient Email"
          className="bg-white/5 border-white/10 text-white placeholder:text-white/30"
          {...register("email", { required: "Recipient email is required", pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "Enter a valid email address" } })}
        />
        {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>}
      </div>

      <div>
        <Input
          placeholder="Subject"
          className="bg-white/5 border-white/10 text-white placeholder:text-white/30"
          {...register("subject", { required: "Subject is required" })}
        />
        {errors.subject && <p className="mt-1 text-xs text-red-400">{errors.subject.message}</p>}
      </div>

      <div>
        <textarea
          className="min-h-[200px] w-full rounded-xl border border-white/10 bg-white/5 p-4 text-white placeholder:text-white/30 focus:outline-none focus:border-indigo-500/50"
          placeholder="Message"
          {...register("body", { required: "Message is required", minLength: { value: 10, message: "Message should be at least 10 characters" } })}
        />
        {errors.body && <p className="mt-1 text-xs text-red-400">{errors.body.message}</p>}
      </div>

      {outreach.isError && (
        <div className="flex items-start gap-2 rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-300">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>
            {outreach.error instanceof Error
              ? (outreach.error as any).response?.data?.detail?.error
                ?? (outreach.error as any).response?.data?.detail
                ?? outreach.error.message
              : "Failed to send outreach. Please try again."}
          </span>
        </div>
      )}

      {outreach.isSuccess && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3 text-sm text-emerald-300">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          Outreach queued successfully.
        </div>
      )}

      <Button type="submit" disabled={isPending} className="w-full">
        {isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
        {isPending ? "Sending..." : "Send Outreach"}
      </Button>
    </form>
  );
}
