"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TicketCreateDialog } from "@/components/tickets/ticket-create-dialog";
import { TicketList } from "@/components/tickets/ticket-list";
import { api } from "@/lib/api";
import { useLeads } from "@/hooks/use-leads";
import { Ticket, Search, Filter, RefreshCw, Plus } from "lucide-react";

export default function TicketsPage() {
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);
  const [selectedLeadEmail, setSelectedLeadEmail] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const { data: leads = [] } = useLeads();

  const loadTickets = async () => {
    setLoading(true);
    try {
      const allTickets: any[] = [];
      const leadArray = leads as any[];
      for (const lead of leadArray.slice(0, 20)) {
        try {
          const resp = await api.get(`/api/leads/${lead.id}/ticket`).catch(() => null);
          if (resp?.data) {
            const ticketData = Array.isArray(resp.data) ? resp.data : resp.data.tickets ? resp.data.tickets : [resp.data];
            allTickets.push(...ticketData.map((t: any) => ({ ...t, lead_id: lead.id, lead_email: lead.email })));
          }
        } catch {}
      }
      setTickets(allTickets);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTickets(); }, [leads]);

  const filteredTickets = tickets.filter((t) =>
    (t.title || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    (t.lead_email || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    (t.department || "").toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = [
    { label: "Total Tickets", value: tickets.length.toString() },
    { label: "Open", value: tickets.filter((t) => t.status === "open" || t.status === "new").length.toString() },
    { label: "In Progress", value: tickets.filter((t) => t.status === "in_progress").length.toString() },
    { label: "Resolved", value: tickets.filter((t) => t.status === "resolved" || t.status === "closed").length.toString() },
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Ticket Center</h1>
            <p className="text-white/50 mt-1">Customer support, escalations, AI handoffs, and voice transfer</p>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={loadTickets} className="p-2 rounded-lg bg-white/5 border border-white/[0.06] text-white/50 hover:text-white hover:bg-white/10 transition-all">
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <div className="flex items-center gap-2 bg-white/5 border border-white/[0.06] rounded-xl px-4 py-2">
              <Search className="w-4 h-4 text-white/40" />
              <input value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search tickets..." className="bg-transparent border-none text-white placeholder:text-white/30 focus:outline-none text-sm w-40" />
            </div>
          </div>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/[0.06] p-4"
            >
              <div className="text-sm text-white/50">{stat.label}</div>
              <div className="mt-1 text-2xl font-bold text-white">{stat.value}</div>
            </motion.div>
          ))}
        </div>

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white">Support Queue</h2>
            <div className="flex gap-2">
              <select
                onChange={(e) => {
                  const lead = (leads as any[]).find((l) => l.id === e.target.value);
                  if (lead) { setSelectedLeadId(lead.id); setSelectedLeadEmail(lead.email); setShowCreate(true); }
                }}
                className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white text-sm"
              >
                <option value="">Select lead for ticket...</option>
                {(leads as any[]).map((lead) => (
                  <option key={lead.id} value={lead.id}>{lead.email} - {lead.name || "No name"}</option>
                ))}
              </select>
            </div>
          </div>

          {showCreate && selectedLeadId && (
            <div className="mb-6 p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/20">
              <TicketCreateDialog leadId={selectedLeadId} leadEmail={selectedLeadEmail} onSuccess={() => { setShowCreate(false); loadTickets(); }} />
            </div>
          )}

          {loading ? (
            <div className="text-center py-8 text-white/50">Loading tickets...</div>
          ) : (
            <TicketList tickets={filteredTickets} onCreateTicket={(leadId, email) => { setSelectedLeadId(leadId); setSelectedLeadEmail(email); setShowCreate(true); }} />
          )}
        </Card>

        <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
          <h2 className="text-lg font-semibold text-white mb-4">Escalation Path</h2>
          <div className="space-y-2">
            {[
              { step: "1", label: "Ticket Created", desc: "AI logs and categorizes the request" },
              { step: "2", label: "AI Resolution Attempt", desc: "Automated response and suggested fix" },
              { step: "3", label: "Human Assignment", desc: "Escalated to appropriate team member" },
              { step: "4", label: "Voice Escalation", desc: "Real-time voice handoff for urgent issues" },
              { step: "5", label: "Barge-In Supervisor", desc: "Supervisor override with full context" },
            ].map((item) => (
              <div key={item.step} className="flex items-center gap-4 p-3 rounded-lg bg-white/5 border border-white/[0.04]">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
                  {item.step}
                </div>
                <div>
                  <div className="text-sm font-medium text-white">{item.label}</div>
                  <div className="text-xs text-white/50">{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}