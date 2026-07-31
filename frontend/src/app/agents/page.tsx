"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bot, Mic, Search, Settings, Play, Pause, BarChart3, MessageSquare, Power, Activity, Sparkles, ChevronRight } from "lucide-react";

interface Agent {
  id: string;
  name: string;
  type: "DISCOVERY" | "QUALIFICATION" | "OUTREACH" | "VOICE";
  status: "active" | "paused" | "error";
  description: string;
  stats: { leads: number; conversations: number; success_rate: number };
  capabilities: string[];
}

const AGENTS: Agent[] = [
  {
    id: "agent-1",
    name: "Discovery Agent",
    type: "DISCOVERY",
    status: "active",
    description: "Autonomously discovers and validates new leads from multiple sources including web searches, social media, and business directories.",
    stats: { leads: 247, conversations: 189, success_rate: 76 },
    capabilities: ["Web scraping", "Social media mining", "Business directory search", "Email discovery", "Company enrichment"],
  },
  {
    id: "agent-2",
    name: "Qualification Agent",
    type: "QUALIFICATION",
    status: "active",
    description: "Screens and scores leads using AI-powered qualification criteria. Prioritizes high-value opportunities automatically.",
    stats: { leads: 156, conversations: 98, success_rate: 89 },
    capabilities: ["Lead scoring", "Intent analysis", "Budget assessment", "Timeline prediction", "Auto-qualification"],
  },
  {
    id: "agent-3",
    name: "Outreach Agent",
    type: "OUTREACH",
    status: "paused",
    description: "Executes multi-channel outreach campaigns across email, SMS, and social. Personalizes every message using lead context.",
    stats: { leads: 89, conversations: 234, success_rate: 68 },
    capabilities: ["Email campaigns", "SMS sequences", "Social DMs", "A/B testing", "Follow-up automation"],
  },
  {
    id: "agent-4",
    name: "Voice Agent",
    type: "VOICE",
    status: "active",
    description: "Handles inbound and outbound voice conversations using natural language. Supports barge-in, call transfers, and real-time transcription.",
    stats: { leads: 45, conversations: 312, success_rate: 92 },
    capabilities: ["Voice calls", "Real-time transcription", "Sentiment analysis", "Barge-in support", "Call scheduling"],
  },
];

export default function AgentsPage() {
  const [agents, setAgents] = useState(AGENTS);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredAgents = agents.filter(
    (a) => a.name.toLowerCase().includes(searchQuery.toLowerCase()) || a.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const toggleAgentStatus = (id: string) => {
    setAgents((prev) => prev.map((a) => (a.id === id ? { ...a, status: a.status === "active" ? "paused" : "active" } : a)));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-emerald-500";
      case "paused": return "bg-amber-500";
      case "error": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getAgentIcon = (type: string) => {
    switch (type) {
      case "VOICE": return Mic;
      default: return Bot;
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Agent Center</h1>
            <p className="text-white/50 mt-1">Orchestrate your AI workforce — manage, monitor, and deploy autonomous agents</p>
          </div>
          <div className="flex items-center gap-3 bg-white/5 border border-white/[0.06] rounded-xl px-4 py-2">
            <Search className="w-4 h-4 text-white/40" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search agents..."
              className="bg-transparent border-none text-white placeholder:text-white/30 focus:outline-none text-sm w-40"
            />
          </div>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-4">
          {[
            { label: "Total Agents", value: agents.length.toString(), icon: Bot },
            { label: "Active", value: agents.filter((a) => a.status === "active").length.toString(), icon: Activity },
            { label: "Leads Generated", value: agents.reduce((s, a) => s + a.stats.leads, 0).toString(), icon: BarChart3 },
            { label: "Conversations", value: agents.reduce((s, a) => s + a.stats.conversations, 0).toString(), icon: MessageSquare },
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

        {filteredAgents.length === 0 ? (
          <Card className="p-12 text-center bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <Bot className="w-12 h-12 mx-auto text-white/20 mb-4" />
            <div className="text-lg font-semibold text-white">No agents found</div>
            <div className="mt-1 text-sm text-white/50">Try a different search term.</div>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {filteredAgents.map((agent, i) => {
              const AgentIcon = getAgentIcon(agent.type);
              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="group bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-6 hover:border-indigo-500/30 transition-all cursor-pointer"
                  onClick={() => setSelectedAgent(selectedAgent?.id === agent.id ? null : agent)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${agent.type === "VOICE" ? "bg-gradient-to-br from-purple-600 to-pink-600" : "bg-gradient-to-br from-indigo-600 to-purple-600"}`}>
                        <AgentIcon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                          <span className="text-xs capitalize text-white/50">{agent.status}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleAgentStatus(agent.id); }}
                        className={`p-2 rounded-lg transition-colors ${agent.status === "active" ? "bg-amber-500/20 text-amber-400 hover:bg-amber-500/30" : "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"}`}
                      >
                        {agent.status === "active" ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      </button>
                      <button className="p-2 rounded-lg bg-white/5 text-white/50 hover:bg-white/10 transition-colors">
                        <Settings className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <p className="text-sm text-white/60 mb-4 line-clamp-2">{agent.description}</p>

                  <div className="grid grid-cols-3 gap-3 mb-4">
                    <div className="text-center p-2 rounded-lg bg-white/5">
                      <div className="text-sm font-semibold text-white">{agent.stats.leads}</div>
                      <div className="text-xs text-white/40">Leads</div>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-white/5">
                      <div className="text-sm font-semibold text-white">{agent.stats.conversations}</div>
                      <div className="text-xs text-white/40">Conversations</div>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-white/5">
                      <div className="text-sm font-semibold text-emerald-400">{agent.stats.success_rate}%</div>
                      <div className="text-xs text-white/40">Success</div>
                    </div>
                  </div>

                  <AnimatePresence>
                    {selectedAgent?.id === agent.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="pt-4 border-t border-white/[0.06]">
                          <h4 className="text-sm font-medium text-white/70 mb-2">Capabilities</h4>
                          <div className="flex flex-wrap gap-2">
                            {agent.capabilities.map((cap) => (
                              <span key={cap} className="px-2 py-1 text-xs rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                                {cap}
                              </span>
                            ))}
                          </div>
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