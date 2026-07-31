"use client";

import { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Play, Pause, SkipForward, ChevronRight, BrainCircuit } from "lucide-react";
import Link from "next/link";
import { RAGVisualization } from "@/components/rag/rag-visualization";

const DEMO_STEPS = [
  {
    id: "discovery",
    title: "Voice Discovery",
    description: "Tell Genesis about your business idea. Our AI understands your vision, industry, and goals through natural conversation.",
    icon: Mic,
    script: "I want to start a premium coaching business for executive women, focusing on leadership development and career transitions.",
  },
  {
    id: "setup",
    title: "AI-Powered Setup",
    description: "Genesis automatically configures your CRM, lead workflows, voice agent personality, and compliance guardrails — all from your conversation.",
    icon: Play,
    script: "Analyzing your industry... configuring CRM pipeline... setting up voice agent with professional tone... establishing compliance rules...",
  },
  {
    id: "launch",
    title: "Launch & Monitor",
    description: "Go live instantly. Monitor lead generation, campaign performance, and agent activity from your dashboard.",
    icon: SkipForward,
    script: "Business launched successfully. Your AI voice agent is now handling inbound leads 24/7.",
  },
];

export default function DemoPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [displayedText, setDisplayedText] = useState("");
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const currentStep = DEMO_STEPS[activeStep];
  const isFirst = activeStep === 0;
  const isLast = activeStep === DEMO_STEPS.length - 1;

  const playStep = useCallback(() => {
    setIsPlaying(true);
    setDisplayedText("");
    const text = currentStep.script;
    let i = 0;
    intervalRef.current = setInterval(() => {
      i++;
      setDisplayedText(text.slice(0, i));
      if (i >= text.length) {
        if (intervalRef.current) clearInterval(intervalRef.current);
        setIsPlaying(false);
      }
    }, 30);
  }, [currentStep.script]);

  const skipStep = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setIsPlaying(false);
    setDisplayedText(currentStep.script);
  }, [currentStep.script]);

  const nextStep = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setIsPlaying(false);
    setDisplayedText("");
    if (!isLast) setActiveStep((s) => s + 1);
  }, [isLast]);

  const prevStep = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setIsPlaying(false);
    setDisplayedText("");
    if (!isFirst) setActiveStep((s) => s - 1);
  }, [isFirst]);

  const StepIcon = currentStep.icon;

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950/90 to-gray-950 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-violet-500/15 via-transparent to-transparent" />

      <div className="relative z-10 mx-auto max-w-4xl px-6 py-24 text-center">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 tracking-tight">
            See Genesis in{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              Action
            </span>
          </h1>
          <p className="text-xl text-white/60 mb-16 max-w-2xl mx-auto leading-relaxed">
            Watch how Genesis uses constitutional voice AI to launch, manage, and grow your business
            — all from a single conversation.
          </p>
        </motion.div>

        <div className="flex gap-2 mb-8 justify-center">
          {DEMO_STEPS.map((step, i) => (
            <button
              key={step.id}
              onClick={() => { if (!isPlaying) { setActiveStep(i); setDisplayedText(""); } }}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
                i === activeStep
                  ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                  : "text-white/40 hover:text-white/60 border border-transparent"
              }`}
              disabled={isPlaying}
            >
              {i + 1}. {step.title}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-8 md:p-12 shadow-2xl shadow-black/50"
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 shrink-0">
                <StepIcon className="w-7 h-7 text-white" />
              </div>
              <div className="text-left">
                <h2 className="text-2xl font-bold text-white">{currentStep.title}</h2>
                <p className="text-white/50 text-sm">{currentStep.description}</p>
              </div>
            </div>

            <div className="bg-black/30 rounded-xl p-6 min-h-[120px] flex items-center border border-white/[0.04] mb-8">
              <div className="flex items-start gap-4 w-full">
                <div className="w-10 h-10 rounded-full bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-1">
                  <Mic className="w-5 h-5 text-indigo-300" />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm text-indigo-300/60 mb-2 font-medium">AI Voice Agent</p>
                  {displayedText ? (
                    <p className="text-white/90 leading-relaxed">
                      {displayedText}
                      {isPlaying && <span className="animate-pulse text-indigo-400">|</span>}
                    </p>
                  ) : (
                    <p className="text-white/30 italic">
                      Press Play to hear how Genesis responds...
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-center gap-4">
              {!isFirst && (
                <button
                  onClick={prevStep}
                  className="px-4 py-2 text-white/50 hover:text-white/70 font-medium transition-colors"
                >
                  Previous
                </button>
              )}

              {!isPlaying && !displayedText && (
                <motion.button
                  onClick={playStep}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all flex items-center gap-2"
                >
                  <Play className="w-5 h-5" />
                  Play Demo
                </motion.button>
              )}

              {isPlaying && (
                <motion.button
                  onClick={skipStep}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-all flex items-center gap-2"
                >
                  <SkipForward className="w-5 h-5" />
                  Skip
                </motion.button>
              )}

              {!isPlaying && displayedText && !isLast && (
                <motion.button
                  onClick={nextStep}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all flex items-center gap-2"
                >
                  Next Step
                  <ChevronRight className="w-5 h-5" />
                </motion.button>
              )}

              {!isPlaying && displayedText && isLast && (
                <motion.button
                  onClick={prevStep}
                  whileTap={{ scale: 0.95 }}
                  className="px-4 py-2 text-white/50 hover:text-white/70 font-medium transition-colors"
                >
                  Replay
                </motion.button>
              )}
            </div>
          </motion.div>
        </AnimatePresence>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-16 bg-white/[0.02] backdrop-blur-xl rounded-2xl border border-white/[0.06] p-8 shadow-2xl shadow-black/30"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
              <BrainCircuit className="w-5 h-5 text-white" />
            </div>
            <div className="text-left">
              <h3 className="text-lg font-semibold text-white">RAG Processing Pipeline</h3>
              <p className="text-sm text-white/50">Real-time retrieval-augmented generation visualization</p>
            </div>
          </div>
          <div className="h-48 md:h-64">
            <RAGVisualization className="w-full h-full" />
          </div>
          <p className="mt-4 text-xs text-white/40 text-center">
            Each node represents a stage in the AI reasoning pipeline — from query embedding through vector search to LLM inference
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-16"
        >
          <Link
            href="/onboarding"
            className="group relative inline-block px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all duration-300 text-lg overflow-hidden"
          >
            <span className="relative z-10">Start Free — No Credit Card</span>
            <div className="absolute inset-0 -translate-x-full group-hover:translate-x-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700" />
          </Link>
        </motion.div>
      </div>
    </main>
  );
}