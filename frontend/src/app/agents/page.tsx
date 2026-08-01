"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Bot, Mic, Search, Play, BarChart3, MessageSquare, Activity, RefreshCw, Loader2, CheckCircle2, XCircle } from "lucide-react";

interface Agent {
  id: string;
  name: string;
  type: string;
  registered: boolean;
  implemented: boolean;
  capabilities: string[];
  domains: string[];
  tools: string[];
  data_access: string[];
  status: string;
}

interface TestResult {
  running: boolean;
  success?: boolean;
  output?: string;
  error?: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<Record<string, TestResult>>({});

  const loadAgents = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/agents");
      if (!res.ok) throw new Error(`Agents API ${res.status}`);
      const data = await res.json();
      setAgents(data.agents || []);
    } catch (e) {
      console.error("Failed to load agents", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
  }, []);

  const runTest = async (agentId: string) => {
    setTestResult((prev) => ({ ...prev, [agentId]: { running: true } }));
    try {
      const res = await fetch(`/api/agents/${agentId}/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: "Briefly summarize what you do and how you help founders." }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Test failed (${res.status})`);
      }
      const data = await res.json();
      const inner = data.result?.result || data.result || {};
      const success = Boolean(data.success && inner.success !== false);
      const output = JSON.stringify(
        inner.result && (inner.result.angles || inner.result.messages || inner.result.response)
          ? inner.result
          : inner,
        null,
        2
      );
      setTestResult((prev) => ({ ...prev, [agentId]: { running: false, success, output } }));
    } catch (e: any) {
      setTestResult((prev) => ({ ...prev, [agentId]: { running: false, success: false, error: String(e.message || e) } }));
    }
  };

  const implemented = agents.filter((a) => a.registered);
  const filtered = agents.filter(
    (a) =>
      a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const activeCount = agents.filter((a) => a.status === "active").length;

  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Agent Center</h1>
            <p className="text-white/50 mt-1">Your production AI workforce — monitored and executed through the Genesis agent runtime</p>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={loadAgents} className="p-2 rounded-lg bg-white/5 border border-white/[0.06] text-white/50 hover:text-white hover:bg-white/10 transition-all">
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <div className="flex items-center gap-2 bg-white/5 border border-white/[0.06] rounded-xl px-4 py-2">
              <Search className="w-4 h-4 text-white/40" />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search agents..."
                className="bg-transparent border-none text-white placeholder:text-white/30 focus:outline-none text-sm w-40"
              />
            </div>
          </div>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-4">
          {[
            { label: "Total Agents", value: agents.length.toString(), icon: Bot },
            { label: "Active", value: activeCount.toString(), icon: Activity },
            { label: "Implemented", value: implemented.length.toString(), icon: CheckCircle2 },
            { label: "Capabilities", value: agents.reduce((s, a) => s + (a.capabilities?.length || 0), 0).toString(), icon: BarChart3 },
          ].map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label} className="p-4 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-white/50">{stat.label}</div>
                  <Icon className="w-4 h-4 text-white/30" />
                </div>
                <div className="mt-2 text-2xl font-bold text-white">{stat.value}</div>
              </Card>
            );
          })}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16 text-white/50">
            <Loader2 className="w-5 h-5 animate-spin mr-2" /> Loading agents...
          </div>
        ) : filtered.length === 0 ? (
          <Card className="p-12 text-center bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <Bot className="w-12 h-12 mx-auto text-white/20 mb-4" />
            <div className="text-lg font-semibold text-white">No agents found</div>
            <div className="mt-1 text-sm text-white/50">Try a different search term.</div>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {filtered.map((agent, i) => {
              const AgentIcon = agent.id === "voice_agent" || agent.id === "landing_agent" || agent.id === "onboarding_agent" ? Mic : Bot;
              const result = testResult[agent.id];
              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-6 hover:border-indigo-500/30 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${agent.id.includes("voice") || agent.id.includes("landing") || agent.id.includes("onboarding") ? "bg-gradient-to-br from-purple-600 to-pink-600" : "bg-gradient-to-br from-indigo-600 to-purple-600"}`}>
                        <AgentIcon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <div className={`w-2 h-2 rounded-full ${agent.status === "active" ? "bg-emerald-500" : "bg-white/20"}`} />
                          <span className="text-xs capitalize text-white/50">
                            {agent.registered ? (agent.status === "active" ? "active" : "idle") : "not registered"}
                          </span>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => runTest(agent.id)}
                      disabled={!agent.registered || result?.running}
                      className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed text-xs font-medium"
                    >
                      {result?.running ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                      {result?.running ? "Running..." : "Test Agent"}
                    </button>
                  </div>

                  <p className="text-sm text-white/60 mb-4 line-clamp-2">{agent.type}</p>

                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {(agent.capabilities?.length ? agent.capabilities : agent.tools).slice(0, 6).map((cap) => (
                      <span key={cap} className="px-2 py-1 text-xs rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                        {cap}
                      </span>
                    ))}
                    <span className="px-2 py-1 text-xs rounded-lg bg-white/5 text-white/40 border border-white/10">
                      {agent.domains?.join(", ") || "no domain"}
                    </span>
                  </div>

                  <button
                    onClick={() => setExpanded(expanded === agent.id ? null : agent.id)}
                    className="text-xs text-indigo-300 hover:text-indigo-200 transition-colors"
                  >
                    {expanded === agent.id ? "Hide details" : "View identity & permissions"}
                  </button>

                  <AnimatePresence>
                    {expanded === agent.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="pt-4 mt-3 border-t border-white/[0.06] space-y-3">
                          <div>
                            <div className="text-xs font-medium text-white/50 mb-1">Tool allowlist</div>
                            <div className="flex flex-wrap gap-1.5">
                              {agent.tools.map((t) => (
                                <span key={t} className="px-2 py-0.5 text-xs rounded bg-white/5 text-white/60 font-mono">{t}</span>
                              ))}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs font-medium text-white/50 mb-1">Data access</div>
                            <div className="flex flex-wrap gap-1.5">
                              {agent.data_access?.map((d) => (
                                <span key={d} className="px-2 py-0.5 text-xs rounded bg-white/5 text-white/60 font-mono">{d}</span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <AnimatePresence>
                    {result && !result.running && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                      >
                        <div className={`mt-4 rounded-xl border p-3 text-xs font-mono max-h-48 overflow-y-auto ${result.success ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-200" : "bg-red-500/5 border-red-500/20 text-red-300"}`}>
                          <div className="flex items-center gap-2 mb-2">
                            {result.success ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                            <span className="font-semibold">{result.success ? "Agent executed successfully" : "Agent execution failed"}</span>
                          </div>
                          <pre className="whitespace-pre-wrap">{result.error || result.output}</pre>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </AppShell>
  );
}
