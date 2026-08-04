"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { VoiceWaveform } from "@/components/voice";
import { Mic, X, Volume2 } from "lucide-react";
import {
  BargeInDetector,
  isMeaningfulUtterance,
  rmsFromFloat32,
  VOICE_CONSTANTS,
} from "@/lib/voice-engine";

interface VoiceLandingAgentProps {
  sessionId?: string;
  onSessionStart?: (sessionId: string) => void;
}

interface ChatMessage {
  role: "assistant" | "user";
  text: string;
}

interface SessionResponse {
  session_id: string;
  visitor_id: string;
  greeting: string;
  greeting_audio_b64?: string | null;
}

interface MessageResponse {
  session_id: string;
  reply: string;
  reply_audio_b64?: string | null;
  intent: string;
}

interface LeadCaptureResponse {
  created: boolean;
  lead_id?: string | null;
  email: string;
}

interface SpeechRecognitionResultItem {
  0: { transcript: string };
  isFinal: boolean;
}

interface SpeechRecognitionEventLike {
  resultIndex: number;
  results: ArrayLike<SpeechRecognitionResultItem>;
}

interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start: () => void;
  stop: () => void;
}

type SpeechRecognitionCtor = new () => SpeechRecognitionLike;

async function fetchWithTimeout(url: string, options: RequestInit, ms: number) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    window.clearTimeout(timer);
  }
}

const QUICK_ACTIONS = [
  {
    label: "Qualify leads",
    hint: "Find qualified prospects",
    text: "I need help qualifying leads for my business.",
  },
  {
    label: "Business launch",
    hint: "Start your company",
    text: "I want to launch my business with Genesis.",
  },
  {
    label: "Pricing",
    hint: "See plans and pricing",
    text: "What are the pricing plans?",
  },
  {
    label: "Contact me",
    hint: "Leave your email",
    text: "Please contact me, I want to leave my email.",
  },
];

export function VoiceLandingAgent({ onSessionStart }: VoiceLandingAgentProps) {
  const [state, setState] = useState<"idle" | "listening" | "speaking" | "thinking">("idle");
  const [sessionActive, setSessionActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [interimTranscript, setInterimTranscript] = useState("");
  const [audioData, setAudioData] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [listening, setListening] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [showLeadCapture, setShowLeadCapture] = useState(false);
  const [leadCaptured, setLeadCaptured] = useState(false);

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const animationRef = useRef<number | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const restartRecognitionRef = useRef<boolean>(false);
  const recognitionGatedRef = useRef<boolean>(true);
  const speakingRef = useRef<boolean>(false);
  const busyRef = useRef<boolean>(false);
  const sessionIdRef = useRef<string | null>(null);
  const sessionActiveRef = useRef<boolean>(false);
  const micHasAecRef = useRef<boolean>(true);
  const bargeInRef = useRef<BargeInDetector>(
    new BargeInDetector({ holdFrames: VOICE_CONSTANTS.BARGE_IN_HOLD_FRAMES })
  );
  const cancelSpeakingRef = useRef<() => void>(() => {});
  const sendMessageRef = useRef<(text: string, role?: "user" | "assistant") => void>(() => {});
  const resumeListeningRef = useRef<() => void>(() => {});

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const startSpeechRecognition = useCallback(() => {
    if (recognitionGatedRef.current) return;
    const w = window as unknown as {
      SpeechRecognition?: SpeechRecognitionCtor;
      webkitSpeechRecognition?: SpeechRecognitionCtor;
    };
    const Ctor = w.SpeechRecognition ?? w.webkitSpeechRecognition;
    if (!Ctor) {
      setListening(true);
      return;
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        /* ignore */
      }
    }
    const recognition = new Ctor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognitionRef.current = recognition;

    recognition.onresult = (event) => {
      if (recognitionGatedRef.current) return;
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) final += event.results[i][0].transcript;
      }
      if (final && isMeaningfulUtterance(final)) {
        setInterimTranscript("");
        sendMessageRef.current(final.trim());
        return;
      }
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (!event.results[i].isFinal) interim += event.results[i][0].transcript;
      }
      setInterimTranscript(interim);
    };

    recognition.onend = () => {
      setListening(false);
      if (restartRecognitionRef.current && sessionActiveRef.current) {
        try {
          recognition.start();
          setListening(true);
        } catch {
          /* restart on next turn */
        }
      }
    };

    recognition.onerror = () => {
      /* keep listening through transient errors */
    };

    try {
      recognition.start();
      setListening(true);
    } catch {
      /* ignore */
    }
  }, []);

  const resumeListening = useCallback(() => {
    if (!sessionActiveRef.current || speakingRef.current) return;
    recognitionGatedRef.current = false;
    restartRecognitionRef.current = true;
    startSpeechRecognition();
  }, [startSpeechRecognition]);

  useEffect(() => {
    resumeListeningRef.current = resumeListening;
  }, [resumeListening]);

  const speak = useCallback(
    (audioB64?: string | null, text?: string) => {
      return new Promise<void>((resolve) => {
        let settled = false;
        const finish = (interrupted: boolean) => {
          if (settled) return;
          settled = true;
          if (speakTimer) window.clearTimeout(speakTimer);
          speakingRef.current = false;
          setState("listening");
          bargeInRef.current.reset();
          cancelSpeakingRef.current = () => {};
          if (interrupted) {
            resumeListeningRef.current();
          } else {
            window.setTimeout(() => {
              if (!speakingRef.current && sessionActiveRef.current) {
                resumeListeningRef.current();
              }
            }, VOICE_CONSTANTS.POST_SPEECH_COOLDOWN_MS);
          }
          resolve();
        };
        const cancel = () => {
          if (audioElementRef.current) {
            audioElementRef.current.pause();
            audioElementRef.current = null;
          }
          if ("speechSynthesis" in window) speechSynthesis.cancel();
          finish(true);
        };
        cancelSpeakingRef.current = cancel;

        // Watchdog: never allow the assistant to appear stuck "speaking".
        let speakTimer: number | null = null;
        const maxSpeakMs = 30000;
        speakTimer = window.setTimeout(() => {
          if (audioElementRef.current) audioElementRef.current.pause();
          if ("speechSynthesis" in window) speechSynthesis.cancel();
          finish(false);
        }, maxSpeakMs);

        recognitionGatedRef.current = true;
        restartRecognitionRef.current = false;
        if (recognitionRef.current) {
          recognitionRef.current.onend = null;
          recognitionRef.current.onresult = null;
          try {
            recognitionRef.current.stop();
          } catch {
            /* ignore */
          }
          recognitionRef.current = null;
        }
        setListening(false);

        const fallback = () => {
          if (settled) return;
          if (text && "speechSynthesis" in window) {
            speakingRef.current = true;
            setState("speaking");
            const utter = new SpeechSynthesisUtterance(text);
            utter.onend = () => finish(false);
            utter.onerror = () => finish(false);
            speechSynthesis.speak(utter);
          } else {
            finish(false);
          }
        };

        if (audioB64) {
          try {
            const audio = new Audio(`data:audio/mp3;base64,${audioB64}`);
            audioElementRef.current = audio;
            speakingRef.current = true;
            setState("speaking");
            audio.onended = () => finish(false);
            audio.onerror = fallback;
            audio.play().catch(fallback);
            return;
          } catch {
            fallback();
          }
        } else {
          fallback();
        }
      });
    },
    []
  );

  const sendMessage = useCallback(
    async (text: string, role: "user" | "assistant" = "user") => {
      if (busyRef.current) return;
      busyRef.current = true;
      setError(null);
      setMessages((prev) => [...prev, { role, text }]);
      setInterimTranscript("");

      const sid = sessionIdRef.current;
      if (!sid) {
        busyRef.current = false;
        return;
      }

      try {
        setState("thinking");
        const response = await fetchWithTimeout(
          "/api/voice/message",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sid, text }),
          },
          60000
        );
        if (!response.ok) throw new Error(`Voice API ${response.status}`);
        const data: MessageResponse = await response.json();
        setMessages((prev) => [...prev, { role: "assistant", text: data.reply }]);
        const lower = text.toLowerCase();
        const wantsContact =
          /contact|reach out|call me|follow up|get in touch|talk to|email me|my email|my name|leave.*(email|info)|speak to someone/.test(
            lower
          );
        if (wantsContact && !leadCaptured) setShowLeadCapture(true);
        await speak(data.reply_audio_b64, data.reply);
      } catch (e) {
        console.error("Voice message failed", e);
        setError("Voice response unavailable — I'm still listening, just say it again.");
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: "I'm sorry, I hit a snag connecting. Could you repeat that?",
          },
        ]);
        setState("listening");
        resumeListeningRef.current();
      } finally {
        busyRef.current = false;
      }
    },
    [speak]
  );

  useEffect(() => {
    sendMessageRef.current = sendMessage;
  }, [sendMessage]);

  const captureLead = useCallback(async (email: string, name?: string, company?: string) => {
    if (!email || !email.includes("@")) return false;
    try {
      const response = await fetchWithTimeout(
        "/api/voice/capture",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            name: name || undefined,
            company: company || undefined,
            session_id: sessionIdRef.current || undefined,
          }),
        },
        15000
      );
      if (!response.ok) return false;
      const data: LeadCaptureResponse = await response.json();
      return data.created === true || data.lead_id != null;
    } catch {
      return false;
    }
  }, []);

  const startSession = useCallback(async () => {
    if (sessionActiveRef.current || isStarting) return;
    setIsStarting(true);
    setError(null);
    try {
      const response = await fetchWithTimeout(
        "/api/voice/session",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ greeting_type: "proactive" }),
        },
        20000
      );
      if (!response.ok) throw new Error(`Voice session ${response.status}`);
      const data: SessionResponse = await response.json();
      sessionIdRef.current = data.session_id;
      setSessionId(data.session_id);
      if (onSessionStart) onSessionStart(data.session_id);
      sessionActiveRef.current = true;
      setSessionActive(true);
      setState("listening");
      setMessages([{ role: "assistant", text: data.greeting }]);
      await speak(data.greeting_audio_b64, data.greeting);
    } catch (e) {
      console.error("Voice session start failed", e);
      setError("Voice assistant unavailable right now. Please try again.");
    } finally {
      setIsStarting(false);
    }
  }, [onSessionStart, speak, isStarting]);

  const startMicrophone = useCallback(async () => {
    try {
      if (mediaStreamRef.current) return;
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
        });
        micHasAecRef.current = true;
      } catch {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        micHasAecRef.current = false;
      }
      bargeInRef.current.arm(micHasAecRef.current);
      mediaStreamRef.current = stream;
      const ctx = new AudioContext();
      audioContextRef.current = ctx;
      const an = ctx.createAnalyser();
      an.fftSize = 256;
      analyserRef.current = an;
      const src = ctx.createMediaStreamSource(stream);
      sourceRef.current = src;
      src.connect(an);

      const update = () => {
        if (!analyserRef.current) return;
        const timeDomain = new Float32Array(analyserRef.current.fftSize);
        analyserRef.current.getFloatTimeDomainData(timeDomain);
        if (speakingRef.current) {
          const level = rmsFromFloat32(timeDomain);
          if (bargeInRef.current.feed(level)) {
            cancelSpeakingRef.current();
          }
        } else {
          // Adaptive noise floor: measure ambient audio between turns so the
          // barge-in threshold rises above room noise and never misfires.
          bargeInRef.current.trackNoise(rmsFromFloat32(timeDomain));
        }
        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyserRef.current.getByteFrequencyData(dataArray);
        setAudioData(Array.from(dataArray).slice(0, 32));
        animationRef.current = requestAnimationFrame(update);
      };
      update();
    } catch {
      setListening(true);
    }
  }, []);

  const stopMicrophone = useCallback(() => {
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
    if (sourceRef.current) sourceRef.current.disconnect();
    if (audioContextRef.current) audioContextRef.current.close();
    if (mediaStreamRef.current) mediaStreamRef.current.getTracks().forEach((t) => t.stop());
    audioContextRef.current = null;
    analyserRef.current = null;
    sourceRef.current = null;
    animationRef.current = null;
    mediaStreamRef.current = null;
    setAudioData([]);
  }, []);

  const stopRecognition = useCallback(() => {
    restartRecognitionRef.current = false;
    recognitionGatedRef.current = true;
    if (recognitionRef.current) {
      recognitionRef.current.onend = null;
      recognitionRef.current.onresult = null;
      try {
        recognitionRef.current.stop();
      } catch {
        /* ignore */
      }
      recognitionRef.current = null;
    }
    setListening(false);
  }, []);

  const handleEnd = useCallback(() => {
    stopRecognition();
    stopMicrophone();
    speakingRef.current = false;
    cancelSpeakingRef.current();
    if ("speechSynthesis" in window) speechSynthesis.cancel();
    if (audioElementRef.current) {
      audioElementRef.current.pause();
      audioElementRef.current = null;
    }
    bargeInRef.current.reset();
    setState("idle");
    sessionActiveRef.current = false;
    setSessionActive(false);
    setSessionId(null);
    sessionIdRef.current = null;
    setMessages([]);
    setShowLeadCapture(false);
    setLeadCaptured(false);
    if (sessionId) {
      fetchWithTimeout(
        "/api/voice/end",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId }),
        },
        10000
      ).catch(() => {});
    }
  }, [sessionId, stopMicrophone, stopRecognition]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (!sessionActiveRef.current && !isStarting) startSession();
    }, 2500);
    return () => clearTimeout(timer);
  }, [sessionActive, isStarting, startSession]);

  useEffect(() => {
    return () => {
      stopRecognition();
      stopMicrophone();
      cancelSpeakingRef.current();
      if (audioElementRef.current) audioElementRef.current.pause();
    };
  }, [stopRecognition, stopMicrophone]);

  useEffect(() => {
    if (sessionActive) {
      const timer = setTimeout(() => {
        startMicrophone();
        resumeListeningRef.current();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [sessionActive, startMicrophone]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, interimTranscript]);

  const isActive = state === "listening" || state === "speaking" || state === "thinking";

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
            <div className="relative w-12 h-12 shrink-0">
              <Image
                src="/voice_agent_image_1.png"
                alt="Genesis AI Voice Agent"
                width={48}
                height={48}
                className="rounded-full object-cover ring-2 ring-white/10 w-12 h-12"
              />
              {isActive && (
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-emerald-500 border-2 border-gray-900 rounded-full"
                />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-white text-sm">Genesis Forge Voice</h3>
              <p className="text-xs text-white/50">
                {state === "idle"
                  ? "Starting your guided experience…"
                  : state === "listening"
                    ? "Listening — just speak"
                    : state === "speaking"
                      ? "Speaking… say anything to interrupt"
                      : "Thinking…"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${isActive ? "bg-emerald-400 animate-pulse" : "bg-white/20"} transition-colors`}
              aria-hidden="true"
            />
            <span className="text-xs text-white/50">{isActive ? "Live" : "Offline"}</span>
          </div>
        </div>

        <div className="p-4 border-b border-white/10 min-h-[160px] max-h-[240px] overflow-y-auto">
          {isActive && audioData.length > 0 && (
            <motion.div key="waveform" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-3">
              <VoiceWaveform audioData={audioData} />
            </motion.div>
          )}
          <div className="space-y-3">
            <AnimatePresence initial={false}>
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-xl px-3 py-2 text-sm ${
                      msg.role === "user"
                        ? "bg-indigo-600 text-white"
                        : "bg-white/5 text-white/90"
                    }`}
                  >
                    {msg.text}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            {interimTranscript && (
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-xl px-3 py-2 text-sm bg-white/5 text-white/40 italic">
                  {interimTranscript}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {error && (
          <div className="px-4 py-2 bg-red-500/10 border-b border-red-500/20 text-xs text-red-300">
            {error}
          </div>
        )}

        {showLeadCapture && !leadCaptured && (
          <div className="p-4 border-b border-white/10">
            <p className="text-xs text-white/60 mb-3">
              {sessionActive
                ? "Say or type your email and I'll follow up — or drop it here:"
                : "Leave your email and we'll follow up:"}
            </p>
            <form
              className="flex flex-col gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                const email = (e.currentTarget.elements.namedItem("leadEmail") as HTMLInputElement).value;
                const name = (e.currentTarget.elements.namedItem("leadName") as HTMLInputElement).value;
                captureLead(email, name).then((ok) => {
                  if (ok) {
                    setLeadCaptured(true);
                    if (sessionActive) {
                      speak(
                        null,
                        "Perfect, I've saved your details. Our team will reach out shortly. Anything else I can help with?"
                      );
                    }
                  } else {
                    setError("Couldn't save that email. Please double-check it and try again.");
                  }
                });
              }}
            >
              <input
                type="email"
                name="leadEmail"
                required
                placeholder="you@company.com"
                className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder:text-white/40 focus:outline-none focus:border-indigo-500/40"
              />
              <input
                type="text"
                name="leadName"
                placeholder="Your name (optional)"
                className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder:text-white/40 focus:outline-none focus:border-indigo-500/40"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold rounded-lg hover:from-indigo-500 hover:to-purple-500 transition-colors"
              >
                Save my contact
              </button>
            </form>
          </div>
        )}
        {showLeadCapture && leadCaptured && (
          <div className="px-4 py-3 border-b border-white/10 bg-emerald-500/10 text-xs text-emerald-300">
            You're on the list — our team will reach out. Want to explore now instead?
          </div>
        )}

        <div className="p-4 border-b border-white/10">
          <div className="grid grid-cols-2 gap-2">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.label}
                onClick={() => sendMessage(action.text)}
                disabled={!sessionActive}
                className="p-3 text-left bg-white/5 rounded-lg hover:bg-white/10 hover:border-indigo-500/30 border border-transparent transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <p className="font-medium text-white text-sm">{action.label}</p>
                <p className="text-xs text-white/50">{action.hint}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                if (sessionActive && state !== "idle") handleEnd();
                else startSession();
              }}
              className={`p-3 rounded-full transition-all ${
                state === "listening"
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/25 scale-110"
                  : "bg-white/10 text-white/70 hover:bg-white/20"
              }`}
              aria-label={state === "listening" ? "Stop listening" : "Start listening"}
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
              {state === "speaking" ? "Speaking" : listening ? "Listening" : "Live"}
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
