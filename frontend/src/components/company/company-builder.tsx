"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Building2, Rocket, Loader2, CheckCircle2, XCircle, Download, Check, Boxes } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

interface BuildStage {
  strategy: boolean;
  content: boolean;
  seo: boolean;
  growth: boolean;
}

export function CompanyBuilder() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [building, setBuilding] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function build() {
    if (!name.trim()) {
      alert("Business name is required.");
      return;
    }
    setBuilding(true);
    setError(null);
    setResult(null);
    try {
      const resp = await api.post("/api/company/build", {
        business_name: name.trim(),
        business_description: description.trim() || "a service business",
        founder_goal: `Launch and grow ${name.trim()}`,
      });
      setResult(resp.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Company build failed. Try again.");
    } finally {
      setBuilding(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-white/70 mb-1">Business Name</label>
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="GreenScape Landscaping"
            className="bg-white/5 border-white/10 text-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-white/70 mb-1">What does it do?</label>
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="residential lawn care in Austin, TX"
            className="bg-white/5 border-white/10 text-white"
          />
        </div>
      </div>

      <Button
        onClick={build}
        disabled={building}
        className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500"
      >
        {building ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Building with Agent Swarm...
          </>
        ) : (
          <>
            <Rocket className="w-4 h-4 mr-2" /> Build My Company
          </>
        )}
      </Button>

      <AnimatePresence>
        {building && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-sm text-white/60">
            Running strategy, content, SEO, and growth agents in parallel (this takes a couple of minutes)...
          </motion.div>
        )}

        {error && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
            {error}
          </motion.div>
        )}

        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 space-y-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="font-semibold text-white">{result.name} — Built</div>
                <div className="text-xs text-white/50">{result.summary}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {Object.entries(result.stages ?? {}).map(([stage, ok]) => (
                <div key={stage} className="flex items-center gap-2 p-2 rounded-lg bg-white/5 border border-white/[0.06]">
                  {ok ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-white/20" />
                  )}
                  <span className="text-xs capitalize text-white/70">{stage}</span>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-white/50 flex items-center gap-1">
                <Boxes className="w-3.5 h-3.5" /> {result.documents?.length ?? 0} documents · ZIP artifact
              </span>
              <a
                href={`/api/company/${result.company_id}/download`}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors"
              >
                <Download className="w-4 h-4" /> Download Company Package
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
