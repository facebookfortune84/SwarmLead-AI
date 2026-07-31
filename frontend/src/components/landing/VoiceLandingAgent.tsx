"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { VoiceWaveform } from "@/components/voice";
import { Mic, X, Sparkles, Volume2 } from "lucide-react";

interface VoiceLandingAgentProps {
  sessionId?: string;
  onSessionStart?: (sessionId: string) => void;
}

export function VoiceLandingAgent({ onSessionStart }: VoiceLandingAgentProps) {
  const [state, setState] = useState<"idle" | "listening" | "speaking" | "thinking">("idle");
  const [sessionActive, setSessionActive] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [audioData, setAudioData] = useState<number[]>([]);
  const [imageError, setImageError] = useState(false);

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const animationRef = useRef<number | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<any>(null);

  const cleanupAudio = useCallback(() => {
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
    if (sourceRef.current) sourceRef.current.disconnect();
    if (audioContextRef.current) audioContextRef.current.close();
    if (mediaStreamRef.current) mediaStreamRef.current.getTracks().forEach((t) => t.stop());
    if (recognitionRef.current) { recognitionRef.current.stop(); recognitionRef.current = null; }
    audioContextRef.current = null;
    analyserRef.current = null;
    sourceRef.current = null;
    animationRef.current = null;
    mediaStreamRef.current = null;
    setAudioData([]);
    setInterimTranscript("");
  }, []);

  const startMicrophone = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      const ctx = new AudioContext();
      audioContextRef.current = ctx;
      const an = ctx.createAnalyser();
      an.fftSize = 128;
      analyserRef.current = an;
      const src = ctx.createMediaStreamSource(stream);
      sourceRef.current = src;
      src.connect(an);

      const update = () => {
        if (!analyserRef.current) return;
        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyserRef.current.getByteFrequencyData(dataArray);
        setAudioData(Array.from(dataArray).slice(0, 32));
        animationRef.current = requestAnimationFrame(update);
      };
      update();
    } catch { /* mic access optional */ }
  }, []);

  const startSpeechRecognition = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: any) => {
      let final = "";
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }
      if (final) setTranscript((prev) => prev + final + " ");
      setInterimTranscript(interim);
      if (final) setState("speaking");
    };

    recognition.onerror = () => { /* silent */ };
    recognition.start();
    recognitionRef.current = recognition;
  }, []);

  const startSession = useCallback(async () => {
    setState("listening");
    setSessionActive(true);
    await startMicrophone();
    startSpeechRecognition();

    try {
      const response = await fetch("/api/voice/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ greeting_type: "proactive" }),
      });
      const data = await response.json();
      if (data.session_id && onSessionStart) onSessionStart(data.session_id);
    } catch { /* optional */ }
  }, [onSessionStart, startMicrophone, startSpeechRecognition]);

  const handleEnd = useCallback(() => {
    cleanupAudio();
    setState("idle");
    setSessionActive(false);
  }, [cleanupAudio]);

  useEffect(() => {
    return () => cleanupAudio();
  }, [cleanupAudio]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (!sessionActive) startSession();
    }, 3000);
    return () => clearTimeout(timer);
  }, [sessionActive, startSession]);

  const isActive = state === "listening" || state === "speaking";
  const displayText = transcript + interimTranscript;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 right-6 z-50"
      role="region"
      aria-label="Voice Assistant"
    >
      <div className="w-96 bg-gray-900/90 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl shadow-black/50 overflow-hidden">
        <div className="p-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {imageError ? (
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
                <Mic className="w-6 h-6 text-white" />
              </div>
            ) : (
              <div className="relative w-12 h-12 shrink-0">
                <Image
                  src="/voice_agent_image_1.png"
                  alt="AI Voice Agent"
                  width={48}
                  height={48}
                  onError={() => setImageError(true)}
                  className={`rounded-full object-cover ring-2 transition-all duration-500 ${
                    isActive ? "ring-indigo-500/50 ring-offset-2 ring-offset-gray-900" : "ring-white/10"
                  }`}
                />
                {isActive && (
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-emerald-500 border-2 border-gray-900 rounded-full"
                  />
                )}
              </div>
            )}
            <div>
              <h3 className="font-semibold text-white text-sm">Genesis Assistant</h3>
              <p className="text-xs text-white/50">
                {state === "idle" ? "Tap to start" : state.charAt(0).toUpperCase() + state.slice(1)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isActive ? "bg-emerald-400 animate-pulse" : "bg-white/20"} transition-colors`} aria-hidden="true" />
            <span className="text-xs text-white/50">{isActive ? "Live" : "Offline"}</span>
          </div>
        </div>

        <div className="p-4 border-b border-white/10 min-h-[100px]">
          {isActive && (
            <motion.div
              key="waveform"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-3"
            >
              <VoiceWaveform audioData={audioData} />
            </motion.div>
          )}
          <div className="bg-white/5 rounded-lg p-3 text-sm min-h-[40px]">
            {displayText ? (
              <p className="text-white/90">{displayText}<span className="animate-pulse text-indigo-400">|</span></p>
            ) : isActive ? (
              <p className="text-white/40 italic">Listening... speak to start</p>
            ) : (
              <p className="text-white/40 italic">Voice assistant ready</p>
            )}
          </div>
        </div>

        <div className="p-4 border-b border-white/10">
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setTranscript((p) => p + "I need help qualifying leads for my business. ")}
              className="p-3 text-left bg-white/5 rounded-lg hover:bg-white/10 hover:border-indigo-500/30 border border-transparent transition-all"
            >
              <p className="font-medium text-white text-sm">Qualify leads</p>
              <p className="text-xs text-white/50">Find qualified prospects</p>
            </button>
            <button
              onClick={() => setTranscript((p) => p + "I want to launch my business with Genesis. ")}
              className="p-3 text-left bg-white/5 rounded-lg hover:bg-white/10 hover:border-indigo-500/30 border border-transparent transition-all"
            >
              <p className="font-medium text-white text-sm">Business launch</p>
              <p className="text-xs text-white/50">Start your company</p>
            </button>
          </div>
        </div>

        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => { if (isActive) handleEnd(); else startSession(); }}
              className={`p-3 rounded-full transition-all ${
                state === "listening" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/25 scale-110" : "bg-white/10 text-white/70 hover:bg-white/20"
              }`}
              aria-label={isActive ? "Stop listening" : "Start listening"}
            >
              <Mic className="w-5 h-5" />
            </button>
            <button
              onClick={handleEnd}
              className="p-3 rounded-full bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
              aria-label="End session"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          {isActive && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-1 text-emerald-400 text-xs"
            >
              <Volume2 className="w-3 h-3" />
              Recording
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function VoiceGreeting({
  greeting,
  onDismiss,
  delay = 3000,
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
      <div className="bg-gray-900/90 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl shadow-black/50 overflow-hidden">
        <div className="p-4 flex items-start gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shrink-0">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-white">Genesis Assistant</p>
            <p className="text-sm text-white/60 mt-1">{greeting}</p>
          </div>
          <button
            onClick={onDismiss}
            className="p-1 rounded-lg hover:bg-white/10 text-white/40 hover:text-white/60 transition-colors"
            aria-label="Dismiss"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}