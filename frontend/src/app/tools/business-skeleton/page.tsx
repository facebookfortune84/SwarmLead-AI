"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { motion } from "framer-motion";
import { Loader2, Zap, FileText, Server, CheckCircle2, Mail } from "lucide-react";

type Manifest = {
  build_id: string;
  intent: string;
  product: string;
  audience: string;
  skeleton: {
    project_slug: string;
    files: Record<string, string>;
    infra_plan: Record<string, string>;
    reversible: boolean;
  };
  status: string;
  next_step: string;
};

export default function BusinessSkeletonTool() {
  const [idea, setIdea] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [leadCaptured, setLeadCaptured] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    if (!idea.trim()) return;
    setLoading(true);
    setError("");
    setManifest(null);
    try {
      const { data } = await api.post("/api/acquisition/skeleton", {
        idea: idea.trim(),
        email: email.trim() || null,
      });
      setManifest(data.manifest);
      setLeadCaptured(!!data.lead_captured);
    } catch (e) {
      setError("Could not generate your skeleton. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0a0a1a] via-[#0d0d24] to-[#0a0a1a] text-white">
      <div className="mx-auto max-w-3xl px-6 py-20">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full text-sm font-medium text-white/80">
            <Zap className="h-4 w-4 text-amber-400" aria-hidden="true" />
            Free tool — no signup required
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Business Skeleton <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">Generator</span>
          </h1>
          <p className="text-white/60 text-lg mb-8">
            Type a business idea. Get the files, infra plan and launch checklist in seconds.
          </p>
        </motion.div>

        <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-6">
          <label className="block">
            <span className="text-sm text-white/70 mb-2 block">Your business idea</span>
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="e.g. An AI coach that helps realtors write listing descriptions"
              rows={3}
              className="w-full rounded-lg border border-white/10 bg-black/30 px-4 py-3 text-white placeholder:text-white/30 focus:border-indigo-400 focus:outline-none"
            />
          </label>
          <label className="block">
            <span className="text-sm text-white/70 mb-2 block flex items-center gap-1">
              <Mail className="h-3.5 w-3.5" aria-hidden="true" /> Email (optional — get the full launch kit)
            </span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="w-full rounded-lg border border-white/10 bg-black/30 px-4 py-3 text-white placeholder:text-white/30 focus:border-indigo-400 focus:outline-none"
            />
          </label>
          <button
            onClick={generate}
            disabled={loading || !idea.trim()}
            className="w-full px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all text-lg"
          >
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <Loader2 className="h-5 w-5 animate-spin" /> Generating…
              </span>
            ) : (
              "Generate my business skeleton"
            )}
          </button>
          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>

        {manifest && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-8 space-y-6">
            {leadCaptured && (
              <div className="flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
                <CheckCircle2 className="h-4 w-4" /> Launch kit on its way — our agents will draft your full setup next.
              </div>
            )}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileText className="h-4 w-4 text-indigo-400" aria-hidden="true" /> Files
              </h2>
              <ul className="space-y-2 text-sm">
                {Object.entries(manifest.skeleton.files).map(([file, desc]) => (
                  <li key={file} className="flex justify-between gap-4 border-b border-white/5 pb-2">
                    <code className="text-white/80">{file}</code>
                    <span className="text-white/50 text-right">{desc}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Server className="h-4 w-4 text-purple-400" aria-hidden="true" /> Infra plan
              </h2>
              <div className="grid grid-cols-3 gap-4 text-sm">
                {Object.entries(manifest.skeleton.infra_plan).map(([k, v]) => (
                  <div key={k}>
                    <div className="text-white/40 uppercase text-xs">{k}</div>
                    <div className="text-white">{v}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <h2 className="text-lg font-semibold mb-2">Next step</h2>
              <p className="text-white/60 text-sm">{manifest.next_step}</p>
              <p className="text-white/40 text-xs mt-2">Build {manifest.build_id} · {manifest.skeleton.reversible ? "fully reversible" : ""}</p>
            </div>
            <a
              href="/onboarding"
              className="block text-center px-6 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-semibold rounded-xl hover:from-emerald-500 hover:to-teal-500 transition-all"
            >
              Provision this business now — no credit card
            </a>
          </motion.div>
        )}
      </div>
    </div>
  );
}
