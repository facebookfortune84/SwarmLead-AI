"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const LEAD_CAPTURE_STORAGE_KEY = "genesis_exit_popup_seen";
const CHECKLIST_EMAILS_KEY = "genesis_checklist_emails";

export function LaunchChecklistMagnet() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "saved" | "error">("idle");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.includes("@")) return;
    try {
      const res = await fetch("/api/voice/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source: "launch_checklist" }),
      });
      if (!res.ok) throw new Error("capture failed");
      const data = await res.json();
      if (data.created === true || data.lead_id != null) {
        setStatus("saved");
        try {
          const seen = JSON.parse(
            localStorage.getItem(CHECKLIST_EMAILS_KEY) || "[]"
          );
          localStorage.setItem(
            CHECKLIST_EMAILS_KEY,
            JSON.stringify([...seen, email])
          );
        } catch {
          /* ignore */
        }
      } else {
        setStatus("saved");
      }
    } catch {
      setStatus("error");
    }
  };

  return (
    <section className="relative py-20 px-6 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-500/10 via-transparent to-transparent" />
      <div className="relative max-w-3xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-white/[0.03] backdrop-blur-xl rounded-3xl border border-white/10 p-10"
        >
          <p className="inline-flex items-center gap-2 rounded-full bg-indigo-500/15 border border-indigo-400/30 px-4 py-1.5 text-xs font-semibold text-indigo-300 mb-6">
            Free for launch week
          </p>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            The 30-Point Launch Checklist
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              used by founders who ship
            </span>
          </h2>
          <p className="text-lg text-white/60 mb-8">
            Domain, DNS, payments, SEO, voice, launch-day rituals — everything
            Genesis Forge checks off before you go live, in one email.
          </p>
          {status === "saved" ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="px-6 py-4 bg-emerald-500/10 border border-emerald-400/30 rounded-2xl text-emerald-300 font-medium"
            >
              You're on the list — the checklist is on its way.
            </motion.div>
          ) : (
            <form onSubmit={submit} className="flex flex-col sm:flex-row gap-3 max-w-xl mx-auto">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="flex-1 px-5 py-3.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/40 focus:outline-none focus:border-indigo-500/40"
                aria-label="Email address"
              />
              <button
                type="submit"
                className="px-6 py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all"
              >
                Send me the checklist
              </button>
            </form>
          )}
          {status === "error" && (
            <p className="mt-3 text-sm text-red-300">
              Couldn't save that — please check your email and try again.
            </p>
          )}
          <p className="mt-4 text-xs text-white/40">
            No spam. One email. Unsubscribe anytime.
          </p>
        </motion.div>
      </div>
    </section>
  );
}

export function ExitIntentPopup() {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "saved" | "error">("idle");
  const armed = useRef(false);

  useEffect(() => {
    const hasSeen = () => {
      try {
        return localStorage.getItem(LEAD_CAPTURE_STORAGE_KEY) === "1";
      } catch {
        return false;
      }
    };
    if (hasSeen()) return;

    const armTimer = window.setTimeout(() => {
      armed.current = true;
    }, 15000);

    const onLeave = (e: MouseEvent) => {
      if (!armed.current) return;
      if (e.clientY <= 0) {
        setOpen(true);
        armed.current = false;
      }
    };
    const onBlur = () => {
      if (!armed.current) return;
      setOpen(true);
      armed.current = false;
    };

    document.addEventListener("mouseout", onLeave);
    window.addEventListener("blur", onBlur);
    return () => {
      window.clearTimeout(armTimer);
      document.removeEventListener("mouseout", onLeave);
      window.removeEventListener("blur", onBlur);
    };
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.includes("@")) return;
    try {
      const res = await fetch("/api/voice/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source: "exit_intent" }),
      });
      if (!res.ok) throw new Error("capture failed");
      const data = await res.json();
      setStatus(data.created === true || data.lead_id != null ? "saved" : "saved");
      try {
        localStorage.setItem(LEAD_CAPTURE_STORAGE_KEY, "1");
      } catch {
        /* ignore */
      }
    } catch {
      setStatus("error");
    }
  };

  const close = () => {
    setOpen(false);
    try {
      localStorage.setItem(LEAD_CAPTURE_STORAGE_KEY, "1");
    } catch {
      /* ignore */
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
          onClick={close}
          role="dialog"
          aria-modal="true"
          aria-label="Before you go"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ type: "spring", damping: 22, stiffness: 300 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-md rounded-3xl border border-white/10 bg-gray-950/95 backdrop-blur-xl p-8 text-center shadow-2xl shadow-black/60"
          >
            <button
              onClick={close}
              className="absolute top-4 right-4 p-2 rounded-full bg-white/5 hover:bg-white/10 text-white/60 transition-colors"
              aria-label="Close"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            {status === "saved" ? (
              <div className="py-8">
                <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-emerald-500/15 border border-emerald-400/30 flex items-center justify-center">
                  <svg className="w-7 h-7 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">See you at launch.</h3>
                <p className="text-white/60 text-sm">
                  We'll send the 30-point checklist and your 1-month-free code.
                </p>
              </div>
            ) : (
              <>
                <p className="inline-flex items-center gap-2 rounded-full bg-indigo-500/15 border border-indigo-400/30 px-4 py-1.5 text-xs font-semibold text-indigo-300 mb-5">
                  Wait — one last thing
                </p>
                <h3 className="text-2xl font-bold text-white mb-3">
                  Founders launching this week get
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-400">
                    {" "}1 month free
                  </span>
                </h3>
                <p className="text-white/60 text-sm mb-6">
                  Drop your email and we'll hold your spot plus send the 30-point
                  launch checklist.
                </p>
                {status === "error" ? (
                  <p className="text-sm text-red-300 mb-4">
                    That email didn't save — please try again.
                  </p>
                ) : (
                  <form onSubmit={submit} className="flex flex-col gap-3">
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@company.com"
                      className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/40 focus:outline-none focus:border-indigo-500/40"
                      aria-label="Email address"
                    />
                    <button
                      type="submit"
                      className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all"
                    >
                      Claim 1 month free
                    </button>
                  </form>
                )}
                <p className="mt-4 text-[11px] text-white/40">
                  No spam — just the checklist and launch updates.
                </p>
              </>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
