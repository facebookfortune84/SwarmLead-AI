export const VOICE_CONSTANTS = {
  /** Post-AEC RMS level (0..1) above which the mic is treated as "user speaking". */
  BARGE_IN_THRESHOLD: 0.06,
  /** Consecutive frames above threshold needed to fire barge-in (rejects short echo spikes). */
  BARGE_IN_ATTACK_FRAMES: 6,
  /** Pause after the assistant finishes speaking before re-enabling speech recognition. */
  POST_SPEECH_COOLDOWN_MS: 450,
  /** Minimum normalized utterance length accepted as real user speech. */
  MIN_UTTERANCE_CHARS: 2,
} as const;

const FILLER_WORDS = new Set(["um", "uh", "er", "hmm", "mm", "huh", "ah", "eh", "oh"]);

export function normalizeUtterance(raw: string): string {
  return raw
    .replace(/[.,!?;:'"()[\]{}\u2018\u2019\u201C\u201D\u2013\u2014]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function isMeaningfulUtterance(
  raw: string,
  minChars: number = VOICE_CONSTANTS.MIN_UTTERANCE_CHARS
): boolean {
  const normalized = normalizeUtterance(raw);
  if (normalized.length < minChars) return false;
  const words = normalized.toLowerCase().split(" ");
  if (words.length === 1 && FILLER_WORDS.has(words[0])) return false;
  return true;
}

/** Normalized RMS (0..1) from a time-domain byte window (AudioContext byte data, 128 = silence). */
export function rmsFromByteTimeDomain(data: Uint8Array): number {
  let sum = 0;
  const mid = 128;
  for (let i = 0; i < data.length; i++) {
    const d = (data[i] - mid) / 128;
    sum += d * d;
  }
  return Math.sqrt(sum / Math.max(data.length, 1));
}

/** Normalized RMS (0..1) from a Float32Array time-domain window (-1..1). */
export function rmsFromFloat32(data: Float32Array): number {
  let sum = 0;
  for (let i = 0; i < data.length; i++) sum += data[i] * data[i];
  return Math.sqrt(sum / Math.max(data.length, 1));
}

export interface BargeInDetectorOptions {
  threshold?: number;
  attackFrames?: number;
}

export class BargeInDetector {
  private readonly threshold: number;
  private readonly attackFrames: number;
  private aboveCount = 0;
  private firedSinceReset = false;

  constructor(opts: BargeInDetectorOptions = {}) {
    this.threshold = opts.threshold ?? VOICE_CONSTANTS.BARGE_IN_THRESHOLD;
    this.attackFrames = opts.attackFrames ?? VOICE_CONSTANTS.BARGE_IN_ATTACK_FRAMES;
  }

  /** Feed one audio level; returns true exactly once when a barge-in is detected. */
  feed(level: number): boolean {
    if (this.firedSinceReset) return false;
    if (level >= this.threshold) {
      this.aboveCount += 1;
      if (this.aboveCount >= this.attackFrames) {
        this.firedSinceReset = true;
        this.aboveCount = 0;
        return true;
      }
    } else {
      this.aboveCount = 0;
    }
    return false;
  }

  /** Prepare for a new speaking turn. */
  reset(): void {
    this.aboveCount = 0;
    this.firedSinceReset = false;
  }
}
