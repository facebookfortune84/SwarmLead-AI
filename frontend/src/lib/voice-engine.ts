export const VOICE_CONSTANTS = {
  /** Post-AEC RMS level (0..1) above which the mic is treated as "user speaking". */
  BARGE_IN_THRESHOLD: 0.06,
  /** Consecutive frames above threshold needed to fire barge-in (rejects short echo spikes). */
  BARGE_IN_ATTACK_FRAMES: 6,
  /** Pause after the assistant finishes speaking before re-enabling speech recognition. */
  POST_SPEECH_COOLDOWN_MS: 450,
  /** Minimum normalized utterance length accepted as real user speech. */
  MIN_UTTERANCE_CHARS: 2,
  /** Frames a barge-in stays latched after the last loud frame (grace period). */
  BARGE_IN_HOLD_FRAMES: 4,
  /** Higher threshold used when the mic does NOT have echo cancellation (no-AEC). */
  BARGE_IN_NO_AEC_THRESHOLD: 0.12,
  /** RMS below this is treated as silence (noise floor clamp). */
  SILENCE_FLOOR: 0.012,
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
  /** Frames to keep the barge-in latched after the last loud frame. */
  holdFrames?: number;
}

export class BargeInDetector {
  private threshold: number;
  private readonly attackFrames: number;
  private readonly holdFrames: number;
  private aboveCount = 0;
  private quietCount = 0;
  private firedSinceReset = false;
  /**
   * Adaptive noise floor (RMS) estimated from ambient frames fed via
   * `trackNoise` while the assistant is NOT speaking. Barge-in thresholds
   * rise above the floor so background room noise / fan hum never triggers
   * an interrupt, while a loud voice always does.
   */
  private noiseFloor = 0.01;
  private readonly noiseDecay = 0.98;
  private readonly noiseCeiling = 0.05;

  constructor(opts: BargeInDetectorOptions = {}) {
    this.threshold = opts.threshold ?? VOICE_CONSTANTS.BARGE_IN_THRESHOLD;
    this.attackFrames = opts.attackFrames ?? VOICE_CONSTANTS.BARGE_IN_ATTACK_FRAMES;
    // 0 = no hold (a single quiet frame resets the attack counter), preserving
    // the original echo-spike-rejection behavior. Callers that want to tolerate
    // brief inter-word pauses pass an explicit holdFrames.
    this.holdFrames = opts.holdFrames ?? 0;
  }

  /** Feed ambient audio while the assistant is NOT speaking (estimates noise). */
  trackNoise(level: number): void {
    // Reject anything that looks like speech relative to the current floor,
    // so a loud burst never gets absorbed as "noise".
    if (level < this.noiseFloor * 2 + 0.04) {
      this.noiseFloor =
        this.noiseFloor * this.noiseDecay + level * (1 - this.noiseDecay);
      this.noiseFloor = Math.min(this.noiseCeiling, Math.max(0.004, this.noiseFloor));
    }
  }

  /** Barge-in threshold that adapts to the measured noise floor. */
  get effectiveThreshold(): number {
    return Math.max(this.threshold, this.noiseFloor * 1.8 + 0.02);
  }

  /**
   * Feed one audio level; returns true exactly once when a barge-in is detected.
   *
   * Uses an attack/hold envelope: the detector must see `attackFrames` loud
   * frames (allowing up to `holdFrames` of quiet frames in between, so short
   * gaps in speech don't reset the attack) to fire. Once fired it stays latched
   * for the rest of the turn, so the agent doesn't resume talking over the user.
   */
  feed(level: number): boolean {
    if (this.firedSinceReset) {
      return false;
    }
    const thresh = this.effectiveThreshold;
    if (level >= thresh) {
      this.aboveCount += 1;
      this.quietCount = 0;
      if (this.aboveCount >= this.attackFrames) {
        this.firedSinceReset = true;
        this.aboveCount = 0;
        return true;
      }
    } else if (this.aboveCount > 0) {
      this.quietCount += 1;
      if (this.quietCount >= this.holdFrames) {
        this.aboveCount = 0;
        this.quietCount = 0;
      }
    }
    return false;
  }

  /** Prepare for a new speaking turn. */
  reset(): void {
    this.aboveCount = 0;
    this.quietCount = 0;
    this.firedSinceReset = false;
  }

  /** Arm the detector for a speech turn given mic quality (AEC available). */
  arm(hasEchoCancellation: boolean): void {
    this.reset();
    this.threshold = hasEchoCancellation
      ? VOICE_CONSTANTS.BARGE_IN_THRESHOLD
      : VOICE_CONSTANTS.BARGE_IN_NO_AEC_THRESHOLD;
  }
}
