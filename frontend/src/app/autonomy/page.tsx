"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  useApproveAction,
  useGrowthQueue,
  useGrowthStatus,
  useRejectAction,
  useRunNow,
  useToggleGrowth,
} from "@/hooks/use-growth";
import {
  Bot,
  CheckCircle2,
  Cpu,
  DollarSign,
  Loader2,
  Mail,
  Play,
  Radio,
  Sparkles,
  XCircle,
} from "lucide-react";

function formatAgo(iso: string | null): string {
  if (!iso) return "Never";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const diff = Date.now() - d.getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return `${Math.max(0, Math.floor(diff / 60000))}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return d.toLocaleDateString();
}

export default function AutonomyPage() {
  const { data: status, isLoading } = useGrowthStatus();
  const { data: queue = [] } = useGrowthQueue();
  const approve = useApproveAction();
  const reject = useRejectAction();
  const runNow = useRunNow();
  const toggle = useToggleGrowth();

  if (isLoading || !status) {
    return (
      <AppShell>
        <div className="flex items-center gap-2 text-white/50 p-8">
          <Loader2 className="h-5 w-5 animate-spin" /> Loading autonomy console…
        </div>
      </AppShell>
    );
  }

  const pending = status.approval_queue;

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white">Autonomy Console</h1>
            <p className="text-white/50 mt-1">
              Full-auto marketing, outreach, SEO and voice tuning — one human gate for sends and quotes.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => toggle.mutate(!status.enabled)}
              disabled={toggle.isPending}
            >
              {status.enabled ? "Pause Auto Mode" : "Resume Auto Mode"}
            </Button>
            <Button onClick={() => runNow.mutate()} disabled={runNow.isPending}>
              <Play className="h-4 w-4 mr-2" /> Run Cycle Now
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/50">Loop Status</span>
              <Radio className="h-4 w-4 text-emerald-400" />
            </div>
            <p className="mt-2 text-2xl font-bold text-white">
              {status.enabled ? "AUTO" : "PAUSED"}
            </p>
            <p className="text-xs text-white/40 mt-1">
              Cycle every {status.cycle_hours}h · {status.cycle_count} cycles run
            </p>
          </Card>
          <Card className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/50">Last Run</span>
              <Cpu className="h-4 w-4 text-blue-400" />
            </div>
            <p className="mt-2 text-2xl font-bold text-white">{formatAgo(status.last_run)}</p>
            <p className="text-xs text-white/40 mt-1">
              {status.artifacts.seo_pages} SEO pages · {status.artifacts.content_drafts} content drafts
            </p>
          </Card>
          <Card className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/50">Human Gate Queue</span>
              <Mail className="h-4 w-4 text-amber-400" />
            </div>
            <p className="mt-2 text-2xl font-bold text-white">{pending.pending}</p>
            <p className="text-xs text-white/40 mt-1">
              {pending.pending_outreach} outreach · {pending.pending_quotes} quotes
            </p>
          </Card>
          <Card className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/50">Learned Voice Tuning</span>
              <Sparkles className="h-4 w-4 text-purple-400" />
            </div>
            <p className="mt-2 text-2xl font-bold text-white">
              {Object.keys(status.learned_keyword_boosts ?? {}).length}
            </p>
            <p className="text-xs text-white/40 mt-1">keyword boosts applied</p>
          </Card>
        </div>

        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Bot className="h-5 w-5 text-emerald-400" />
            <h2 className="text-lg font-semibold text-white">
              Approval Queue <span className="text-white/40 text-sm">— the one human gate</span>
            </h2>
          </div>
          {queue.length === 0 ? (
            <p className="text-sm text-white/40 py-6 text-center">
              Nothing pending. The loop only drafts — you decide what goes out.
            </p>
          ) : (
            <div className="space-y-4">
              {queue.map((item) => (
                <div key={item.id} className="rounded-lg border border-white/10 bg-white/5 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Badge
                        className={
                          item.kind === "quote_send"
                            ? "bg-emerald-500/20 text-emerald-300"
                            : "bg-blue-500/20 text-blue-300"
                        }
                      >
                        {item.kind === "quote_send" ? (
                          <DollarSign className="h-3 w-3 mr-1" />
                        ) : (
                          <Mail className="h-3 w-3 mr-1" />
                        )}
                        {item.kind === "quote_send" ? "Quote" : "Outreach"}
                      </Badge>
                      <span className="text-sm font-medium text-white">
                        {item.payload.lead_name || item.payload.to_email}
                      </span>
                      <span className="text-xs text-white/40">{item.payload.to_email}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        className="bg-emerald-500 hover:bg-emerald-600 text-black"
                        onClick={() => approve.mutate(item.id)}
                        disabled={approve.isPending}
                      >
                        <CheckCircle2 className="h-4 w-4 mr-1" /> Approve & Send
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-red-300 border-red-500/30"
                        onClick={() => reject.mutate(item.id)}
                        disabled={reject.isPending}
                      >
                        <XCircle className="h-4 w-4 mr-1" /> Reject
                      </Button>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-white/70">{item.payload.subject}</p>
                  <pre className="mt-2 whitespace-pre-wrap rounded bg-black/40 p-3 text-xs text-white/60">
                    {item.payload.body}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </AppShell>
  );
}
