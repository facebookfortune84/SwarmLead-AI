"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { VoiceOrb, VoiceWaveform } from "@/components/voice";
import { Mic, X, Sparkles } from "lucide-react";

interface VoiceLandingAgentProps {
  sessionId?: string;
  onSessionStart?: (sessionId: string) => void;
}

export function VoiceLandingAgent({ onSessionStart }: VoiceLandingAgentProps) {
  const [state, setState] = useState<"idle" | "listening" | "speaking" | "thinking">("idle");
  const [sessionActive, setSessionActive] = useState(false);
  const [transcript, setTranscript] = useState("");

  const startSession = useCallback(async () => {
    setSessionActive(true);
    setState("listening");
    
    // Start voice session via API
    try {
      const response = await fetch("/api/voice/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ greeting_type: "proactive" })
      });
      const data = await response.json();
      if (data.session_id && onSessionStart) {
        onSessionStart(data.session_id);
      }
    } catch (e) {
      console.error("Failed to start session:", e);
    }
  }, [onSessionStart]);

  const handleEnd = () => {
    setState("idle");
    setSessionActive(false);
  };

  // Proactive greeting on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!sessionActive) {
        startSession();
      }
    }, 3000);

    return () => clearTimeout(timer);
  }, [sessionActive, startSession]);

  // Scroll trigger
  useEffect(() => {
    const handleScroll = () => {
      if (!sessionActive && window.scrollY > window.innerHeight * 0.5) {
        startSession();
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [sessionActive, startSession]);

  // Exit intent
  useEffect(() => {
    const handleMouseLeave = (e: MouseEvent) => {
      if (!sessionActive && e.clientY <= 0) {
        startSession();
      }
    };

    document.addEventListener("mouseleave", handleMouseLeave);
    return () => document.removeEventListener("mouseleave", handleMouseLeave);
  }, [sessionActive, startSession]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 right-6 z-50"
      role="region"
      aria-label="Voice Assistant"
    >
      <div className="w-96 bg-white/95 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <VoiceOrb state={state} onClick={state === "idle" ? startSession : undefined} />
            <div>
              <h3 className="font-semibold text-gray-900">Genesis Assistant</h3>
              <p className="text-sm text-gray-500">
                {state === "idle" ? "Click to start" : state.charAt(0).toUpperCase() + state.slice(1)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" aria-hidden="true" />
            <span className="text-xs text-gray-500">Live</span>
          </div>
        </div>

        {/* Transcript / Waveform */}
        <div className="p-4 border-b border-gray-100">
          <AnimatePresence mode="wait">
            {state === "listening" || state === "speaking" ? (
              <motion.div
                key="waveform"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-3"
              >
                <VoiceWaveform audioData={[]} />
              </motion.div>
            ) : (
              <motion.div
                key="transcript"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600 min-h-[60px]">
                  {transcript || "Listening..."}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Quick Actions */}
        <div className="p-4 border-b border-gray-100">
          <div className="grid grid-cols-2 gap-2">
            <button className="p-3 text-left bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <p className="font-medium text-gray-900">Qualify leads</p>
              <p className="text-sm text-gray-500">Find qualified prospects</p>
            </button>
            <button className="p-3 text-left bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <p className="font-medium text-gray-900">Business launch</p>
              <p className="text-sm text-gray-500">Start your company</p>
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="p-4 border-t border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setState(state === "listening" ? "idle" : "listening")}
                className={`p-2 rounded-full transition-colors ${
                  state === "listening" ? "bg-primary-100 text-primary-700" : "bg-gray-100 text-gray-600"
                }`}
                aria-label="Toggle listening"
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                onClick={handleEnd}
                className="p-2 rounded-full bg-red-100 text-red-600 hover:bg-red-200 transition-colors"
                aria-label="End session"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export function VoiceGreeting({ 
  greeting, 
  onDismiss, 
  delay = 3000 
}: { 
  greeting: string; 
  onDismiss: () => void;
  delay?: number;
}) {
  useEffect(() => {
    const timer = setTimeout(onDismiss, delay);
    return () => clearTimeout(timer);
  }, [onDismiss, delay]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      className="fixed bottom-6 right-6 z-50 max-w-md"
    >
      <div className="bg-white/95 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-2xl overflow-hidden">
        <div className="p-4 flex items-start gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-700 to-primary-900 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-gray-900">Genesis Assistant</p>
            <p className="text-sm text-gray-600 mt-1">{greeting}</p>
          </div>
          <button
            onClick={onDismiss}
            className="p-1 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Dismiss"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}