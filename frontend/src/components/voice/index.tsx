"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, MicOff, Volume2, X } from "lucide-react";
import { orbState } from "@/design-system/animations/premiumVariants";


interface VoiceOrbProps {
  state: "idle" | "listening" | "speaking" | "thinking";
  onClick?: () => void;
  className?: string;
}

export function VoiceOrb({ state, onClick, className = "" }: VoiceOrbProps) {
  return (
    <motion.div
      className={`relative w-20 h-20 rounded-full bg-gradient-to-br from-primary-700 to-primary-900 flex items-center justify-center cursor-pointer ${className}`}
      onClick={onClick}
      animate={state}
      variants={orbState}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick?.()}
      aria-label={`Voice assistant, currently ${state}`}
    >
      <AnimatePresence mode="wait">
        {state === "listening" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
            className="absolute inset-0 rounded-full border-2 border-gold-400/50 animate-pulse"
          />
        )}
        {state === "speaking" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: [1, 1.15, 1] }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.5, repeat: Infinity, ease: "easeInOut" }}
            className="absolute inset-0 rounded-full bg-gradient-to-br from-gold-400/30 to-gold-600/30"
          />
        )}
      </AnimatePresence>
      
      <div className="relative z-10 flex items-center justify-center">
        <Mic className="w-8 h-8 text-white" />
      </div>
    </motion.div>
  );
}

interface VoiceWaveformProps {
  audioData: number[];
  className?: string;
}

export function VoiceWaveform({ audioData, className = "" }: VoiceWaveformProps) {
  const barCount = 64;
  const barWidth = 3;
  const gap = 2;
  const maxHeight = 60;

  // Generate mock data if not provided
  const data = audioData.length > 0 
    ? audioData 
    : Array.from({ length: barCount }, () => Math.random() * maxHeight);

  return (
    <svg 
      className={`w-full h-20 ${className}`}
      viewBox={`0 0 ${barCount * (barWidth + gap)} ${maxHeight}`}
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#D4A843" />
          <stop offset="100%" stopColor="#B89038" />
        </linearGradient>
      </defs>
      <g>
        {data.map((value, i) => (
          <motion.rect
            key={i}
            x={i * (barWidth + gap)}
            y={maxHeight - Math.max(value, 2)}
            width={barWidth}
            height={Math.max(value, 2)}
            fill="url(#waveGradient)"
            rx={1}
            initial={{ height: 2, y: maxHeight - 2 }}
            animate={{ height: Math.max(value, 2), y: maxHeight - Math.max(value, 2) }}
            transition={{ 
              duration: 0.1, 
              delay: i * 0.005,
              ease: "easeOut"
            }}
          />
        ))}
      </g>
    </svg>
  );
}

interface VoiceControlsProps {
  state: "idle" | "listening" | "speaking" | "thinking";
  onToggle: () => void;
  onEnd: () => void;
  volume?: number;
  onVolumeChange?: (vol: number) => void;
  muted?: boolean;
  onMuteToggle?: () => void;
}

export function VoiceControls({ 
  state, 
  onToggle, 
  onEnd, 
  volume = 1, 
  onVolumeChange,
  muted = false,
  onMuteToggle
}: VoiceControlsProps) {
  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full border border-gray-200 shadow-lg">
      <motion.button
        onClick={onMuteToggle}
        disabled={muted && state === "speaking"}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
        aria-label={muted ? "Unmute" : "Mute"}
      >
        {muted ? <MicOff className="w-5 h-5 text-gray-600" /> : <Volume2 className="w-5 h-5 text-gray-600" />}
      </motion.button>
      
      <div className="flex items-center gap-2">
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={volume}
          onChange={(e) => onVolumeChange?.(parseFloat(e.target.value))}
          className="w-20 h-1 bg-gray-200 rounded-lg appearance-none accent-gold-500 cursor-pointer"
          aria-label="Volume"
        />
      </div>
      
      <AnimatePresence mode="wait">
        {state === "idle" && (
          <motion.button
            key="idle"
            onClick={onToggle}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-700 to-primary-900 flex items-center justify-center text-white shadow-lg hover:shadow-xl transition-shadow"
            aria-label="Start voice session"
          >
            <Mic className="w-6 h-6 mx-auto" />
          </motion.button>
        )}
        
        {state === "listening" && (
          <motion.button
            key="listening"
            onClick={onToggle}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center text-white shadow-lg animate-pulse"
            aria-label="Stop listening"
          >
            <Mic className="w-6 h-6 mx-auto" />
          </motion.button>
        )}
        
        {state === "speaking" && (
          <motion.button
            key="speaking"
            onClick={onEnd}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="w-12 h-12 rounded-full bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center text-white shadow-lg"
            aria-label="End voice session"
          >
            <X className="w-6 h-6 mx-auto" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}

interface VoiceSessionProps {
  session: any;
  onEnd: () => void;
  onMuteToggle: () => void;
  onVolumeChange: (vol: number) => void;
  volume: number;
  muted: boolean;
  state: "idle" | "listening" | "speaking" | "thinking";
  onToggle: () => void;
}

export function VoiceSession({ 
  session, 
  onEnd, 
  onMuteToggle, 
  onVolumeChange, 
  volume, 
  muted, 
  state, 
  onToggle 
}: VoiceSessionProps) {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <VoiceSessionPanel
        session={session}
        onEnd={onEnd}
        onMuteToggle={onMuteToggle}
        onVolumeChange={onVolumeChange}
        volume={volume}
        muted={muted}
        state={state}
        onToggle={onToggle}
      />
    </div>
  );
}

interface VoiceSessionPanelProps {
  session: any;
  onEnd: () => void;
  onMuteToggle: () => void;
  onVolumeChange: (vol: number) => void;
  volume: number;
  muted: boolean;
  state: "idle" | "listening" | "speaking" | "thinking";
  onToggle: () => void;
}

export function VoiceSessionPanel({ 
  session, 
  onEnd, 
  onMuteToggle, 
  onVolumeChange, 
  volume, 
  muted, 
  state, 
  onToggle 
}: VoiceSessionPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      className="w-96 bg-white/95 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-2xl overflow-hidden"
    >
      <div className="p-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-700 to-primary-900 flex items-center justify-center">
            <Mic className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Voice Session</h3>
            <p className="text-sm text-gray-500">{session?.visitor_id || "Anonymous"}</p>
          </div>
        </div>
        
        <VoiceControls
          state={state}
          onToggle={onToggle}
          onEnd={onEnd}
          volume={volume}
          onVolumeChange={onVolumeChange}
          muted={muted}
          onMuteToggle={onMuteToggle}
        />
      </div>
      
      <div className="p-4 space-y-2 max-h-64 overflow-y-auto">
        <div className="text-sm text-gray-500">
          <p>Session: {session?.session_id?.slice(0, 8)}...</p>
          <p>Duration: {session?.duration || 0}s</p>
          <p>Turns: {session?.turn_count || 0}</p>
        </div>
      </div>
    </motion.div>
  );
}

