"use client";

import { motion } from "framer-motion";
import { VoiceOrb, VoiceWaveform } from "@/components/voice";
import { ArrowRight, CheckCircle, Sparkles, Target, Zap, Shield, Users, BarChart3 } from "lucide-react";

interface VoiceLandingAgentProps {
  sessionId?: string;
  onSessionStart?: (sessionId: string) => void;
}

export function VoiceLandingAgent({ sessionId, onSessionStart }: VoiceLandingAgentProps) {
  const [state, setState] = useState<"idle" | "listening" | "speaking" | "thinking">("idle");
  const [showAgent, setShowAgent] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [sessionActive, setSessionActive] = useState(false);

  const startSession = async () => {
    setShowAgent(true);
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
  };

  const handleToggle = () => {
    if (state === "idle" || state === "speaking") {
      setState("listening");
    } else if (state === "listening") {
      setState("speaking");
    }
  };

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
  }, [sessionActive]);

  // Scroll trigger
  useEffect(() => {
    const handleScroll = () => {
      if (!sessionActive && window.scrollY > window.innerHeight * 0.5) {
        startSession();
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [sessionActive]);

  // Exit intent
  useEffect(() => {
    const handleMouseLeave = (e: MouseEvent) => {
      if (!sessionActive && e.clientY <= 0) {
        startSession();
      }
    };

    document.addEventListener("mouseleave", handleMouseLeave);
    return () => document.removeEventListener("mouseleave", handleMouseLeave);
  }, [sessionActive]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 right-6 z-50"
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
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
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
            <button className="p-3 text-left bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-left">
              <p className="font-medium text-gray-900">Qualify leads</p>
              <p className="text-sm text-gray-500">Find qualified prospects</p>
            </button>
            <button className="p-3 text-left bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-left">
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

export function FeatureShowcase() {
  const features = [
    { icon: Voice, title: "Voice-First", desc: "Natural conversations with AI agents" },
    { icon: Zap, title: "Instant Launch", desc: "Business live in minutes, not months" },
    { icon: Shield, title: "Constitutional AI", desc: "Built-in governance & compliance" },
    { icon: Target, title: "Precision Targeting", desc: "AI-powered lead qualification" },
    { icon: BarChart3, title: "Real-time Analytics", desc: "Live conversion funnels & ROI" },
    { icon: Users, title: "Team Collaboration", desc: "Multi-agent workflows" }
  ];

  return (
    <section className="py-20 px-6 max-w-7xl mx-auto">
      <motion.div 
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Why Genesis?
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          The only platform that combines voice AI agents with constitutional governance 
          to autonomously launch and grow your business.
        </p>
      </motion.div>

      <div className="grid md:grid-2 lg:grid-3 gap-8">
        {features.map((feature, i) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            className="group p-8 bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-100 hover:border-gold-300/50 hover:shadow-xl transition-all duration-300"
          >
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-700 to-primary-900 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
              <feature.icon className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-300 mb-2">{feature.title}</h3>
            <p className="text-gray-600 leading-relaxed">{feature.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export function SocialProof() {
  const stats = [
    { value: "10x", label: "Faster Launch" },
    { value: "85%", label: "Lead Conversion" },
    { value: "3min", label: "Avg Setup Time" },
    { value: "99.9%", label: "Uptime SLA" }
  ];

  return (
    <section className="py-16 px-6 max-w-7xl mx-auto bg-gradient-to-r from-primary-900 via-primary-800 to-primary-900 rounded-3xl">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            className="text-center"
          >
            <div className="text-4xl md:text-5xl font-bold text-white mb-2">
              {stat.value}
            </div>
            <div className="text-gold-300 font-medium">{stat.label}</div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export function CTASection() {
  return (
    <section className="py-20 px-6 max-w-7xl mx-auto text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Ready to Launch Your Business?
        </h2>
        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
          Join 10,000+ founders who launched with Genesis. Start free, scale infinitely.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a 
            href="/onboarding" 
            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-primary-700 to-primary-900 text-white font-semibold rounded-xl hover:from-primary-800 hover:to-primary-900 shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <Sparkles className="w-5 h-5" />
            Start Free - No Credit Card
          </a>
          <a 
            href="/demo" 
            className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300"
          >
            Watch Demo
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </motion.div>
    </section>
  );
}