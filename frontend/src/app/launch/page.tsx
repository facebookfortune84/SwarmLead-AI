"use client";

import { useState } from "react";
import {
  Rocket,
  Sparkles,
  Mail,
  Users,
  Bot,
  BadgeDollarSign,
  CheckCircle2,
  Loader2,
  Mic,
  Send,
  Globe,
} from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useConciergeStart, useConciergeTurn } from "@/hooks/use-launch";
import type { ConciergeTurn } from "@/hooks/use-launch";

import { useMaximizeLevers } from "@/hooks/use-launch";

const STEP_ORDER = ["company", "domain", "audience", "roles", "offer", "prompt", "done"];

const STEP_META: Record<
  string,
  { icon: typeof Rocket; title: string; hint: string }
> = {
  company: {
    icon: Sparkles,
    title: "Name & Idea",
    hint: "Describe what you sell and who it's for.",
  },
  domain: { icon: Globe, title: "Domain", hint: "Pick a free domain extension." },
  audience: { icon: Users, title: "Audience", hint: "Who's your ideal buyer?" },
  roles: { icon: Bot, title: "Roles", hint: "Which agents to staff." },
  offer: {
    icon: BadgeDollarSign,
    title: "Offer",
    hint: "What you sell and for how much.",
  },
  prompt: { icon: Rocket, title: "Review", hint: "Review the brief." },
  done: { icon: CheckCircle2, title: "Ready", hint: "Hand off to the swarm." },
};

export default function LaunchPage() {
  const start = useConciergeStart();
  const turn = useConciergeTurn();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [state, setState] = useState<ConciergeTurn | null>(null);
  const [built, setBuilt] = useState(false);
  const [busy, setBusy] = useState(false);
  const [stagedText, setStagedText] = useState("");
  const [transcript, setTranscript] = useState<Array<{ role: string; content: string }>>([]);

  const meta = (state ? STEP_META[state.step] : STEP_META.company) ?? STEP_META.company;

  const kickoff = async () => {
    setBusy(true);
    try {
      const res = await start.mutateAsync({ founder_name: "" });
      setSessionId(res.session_id);
      setState(res);
      setTranscript([{ role: "assistant", content: res.prompt }]);
    } finally {
      setBusy(false);
    }
  };

  const send = async (text: string) => {
    if (!sessionId || !text.trim() || busy) return;
    setBusy(true);
    const reply = [text.trim(), stagedText.trim()].filter(Boolean).join(" ");
    setStagedText("");
    try {
      const res = await turn.mutateAsync({ session_id: sessionId, text: reply });
      setState(res);
      setTranscript((t) => [
        ...t,
        { role: "user", content: reply },
        { role: "assistant", content: res.prompt || "Ready to launch." },
      ]);
      if (res.launch_signal) {
        setBuilt(true);
      }
    } finally {
      setBusy(false);
    }
  };

  const quickTips: Record<string, string[]> = {
    company: [
      "A mobile dog-grooming business",
      "AI tax advisory for freelancers",
      "Landing-page agency for DTC brands",
    ],
    domain: [".com", ".io", ".ai", ".app"],
    roles: ["sdr, outreach, content, seo", "voice, closer, growth"],
    offer: ["premium flat-rate retainer, $499/mo", "free quote, per-project pricing"],
  };

  const chips = quickTips[state?.step ?? "company"] ?? quickTips.company;

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto py-6 px-4">
        <div className="flex items-center gap-3 mb-6">
          <div className="rounded-2xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/10 p-3 border border-white/10">
            <Rocket className="w-6 h-6 text-violet-300" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Launch Studio</h1>
            <p className="text-sm text-white/50">
              Answer the questions below / speak into the mic. Genesis drafts the
              company brief and the swarm builds the whole business from it.
            </p>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* conversation column */}
          <div className="lg:col-span-2 space-y-4">
            {!sessionId ? (
              <Card className="p-8 bg-white/[0.03] backdrop-blur-xl border-white/[0.06] text-center">
                <Sparkles className="w-10 h-10 text-violet-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-white mb-2">
                  Take it from idea to armed swarm
                </h2>
                <p className="text-sm text-white/50 mb-6 max-w-md mx-auto">
                  The concierge walks you through naming, domain, audience, roles,
                  offer — then hands the synthesized brief to the Strategy,
                  Content, SEO and Growth agents to build the whole company.
                </p>
                <Button onClick={kickoff} disabled={busy} className="gap-2">
                  {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Rocket className="w-4 h-4" />}
                  {built ? "Restart" : "Start the launch"}
                </Button>
              </Card>
            ) : (
              <>
                {/* transcript */}
                <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-sm text-white/70 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      AI Launch Optimizer
                    </div>
                    <div className="text-xs rounded-full bg-white/5 px-3 py-1 border border-white/10">
                      {state?.step === "done" ? "Complete" : `Step ${STEP_ORDER.indexOf(state?.step ?? "") + 1} of ${STEP_ORDER.length}`}
                    </div>
                  </div>
                  <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
                    {transcript.map((t, i) => (
                      <div
                        key={i}
                        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                          t.role === "user"
                            ? "ml-auto bg-violet-500/20 border border-violet-500/30 text-white/90"
                            : "bg-white/5 border border-white/10 text-white/80"
                        }`}
                      >
                        {t.content}
                      </div>
                    ))}
                    {busy && (
                      <div className="flex items-center gap-2 text-white/40 text-sm">
                        <Loader2 className="w-4 h-4 animate-spin" /> working...
                      </div>
                    )}
                  </div>
                </Card>

                {/* input */}
                <Card className="p-4 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
                  <div className="text-sm text-white/60 mb-2">
                    <meta.icon className="w-4 h-4 inline mr-2 text-violet-300" />
                    {meta.title}: {meta.hint}
                  </div>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {chips.map((chip) => (
                      <button
                        key={chip}
                        onClick={() => send(chip)}
                        className="text-xs rounded-full bg-white/5 border border-white/10 px-3 py-1.5 text-white/70 hover:bg-white/10 hover:text-white transition"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      value={stagedText}
                      onChange={(e) => setStagedText(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") send(stagedText);
                      }}
                      placeholder="Type or tap a suggestion..."
                      className="flex-1"
                    />
                    <Button disabled={busy || !sessionId} onClick={() => send(stagedText)} className="gap-2">
                      <Send className="w-4 h-4" /> Send
                    </Button>
                  </div>
                  <div className="mt-3 text-xs text-white/40 flex items-center gap-1.5">
                    <Mic className="w-3.5 h-3.5 text-violet-300" /> Voice input is available in the
                    app voice widget — every prompt here is also speakable.
                  </div>
                </Card>
              </>
            )}
          </div>

          {/* right: live brief + optimizer status */}
          <div className="space-y-6">
            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <Mail className="w-4 h-4 text-emerald-400" /> Live company brief
              </h3>
              {state?.brief ? (
                <pre className="whitespace-pre-wrap text-xs text-white/70 leading-relaxed">
                  {state.brief.replaceAll("<br/>", "\n")}
                </pre>
              ) : (
                <p className="text-xs text-white/40">
                  Your answers build up here. Nothing is sent until you approve.
                </p>
              )}
            </Card>

            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-violet-400" /> Outreach optimizer
              </h3>
              <OptimizerLevers />
            </Card>

            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> What happens next
              </h3>
              <ol className="text-xs text-white/60 space-y-2 list-decimal ml-4">
                <li>Brief is saved when you approve.</li>
                <li>Strategy, content, SEO & growth agents build artifacts.</li>
                <li>Launch checklist + workflows are provisioned.</li>
                <li>Discovery loop starts — all sends behind approval.</li>
              </ol>
              {built && (
                <div className="mt-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-3 text-sm text-emerald-200">
                  Launch brief locked in. Head to the Dashboard → Company Builder
                  to generate the full package.
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function OptimizerLevers() {
  const { data } = useMaximizeLevers();
  const levers = (data?.levers ?? []) as Array<{ key: string; label: string; category: string }>;
  return (
    <div className="space-y-2">
      {levers.slice(0, 6).map((l) => (
        <div
          key={l.key}
          className="flex items-center justify-between rounded-lg bg-white/5 border border-white/5 px-3 py-2 text-xs text-white/70"
        >
          <span>{l.label}</span>
          <span className="text-white/35 uppercase text-[10px]">{l.category}</span>
        </div>
      ))}
      <p className="text-[10px] text-white/35 pt-2">{levers.length} levers available for every outreach send.</p>
    </div>
  );
}