import { describe, it, expect } from "vitest";
import {
  BargeInDetector,
  isMeaningfulUtterance,
  normalizeUtterance,
  rmsFromByteTimeDomain,
  rmsFromFloat32,
  VOICE_CONSTANTS,
} from "../voice-engine";

describe("normalizeUtterance", () => {
  it("trims and collapses whitespace", () => {
    expect(normalizeUtterance("  hello   world  ")).toBe("hello world");
  });

  it("strips punctuation", () => {
    expect(normalizeUtterance("Hello, world!")).toBe("Hello world");
  });

  it("strips curly quotes and em dashes", () => {
    expect(normalizeUtterance("\u201CHello\u201D \u2014 world")).toBe("Hello world");
  });
});

describe("isMeaningfulUtterance", () => {
  it("rejects empty or one-char fragments", () => {
    expect(isMeaningfulUtterance("")).toBe(false);
    expect(isMeaningfulUtterance(" ")).toBe(false);
    expect(isMeaningfulUtterance("a")).toBe(false);
  });

  it("rejects short fragments below minChars", () => {
    expect(isMeaningfulUtterance("hi", 3)).toBe(false);
  });

  it("rejects pure filler words", () => {
    expect(isMeaningfulUtterance("um")).toBe(false);
    expect(isMeaningfulUtterance("uh")).toBe(false);
    expect(isMeaningfulUtterance("hmm")).toBe(false);
    expect(isMeaningfulUtterance("mm")).toBe(false);
  });

  it("accepts short greetings and real utterances", () => {
    expect(isMeaningfulUtterance("hi")).toBe(true);
    expect(isMeaningfulUtterance("Help me qualify leads")).toBe(true);
    expect(isMeaningfulUtterance("What are the pricing plans?")).toBe(true);
  });
});

describe("rmsFromByteTimeDomain", () => {
  it("returns 0 for silence", () => {
    const data = new Uint8Array(128).fill(128);
    expect(rmsFromByteTimeDomain(data)).toBeCloseTo(0, 6);
  });

  it("returns ~0.5 for a full-scale square wave", () => {
    const data = new Uint8Array(128);
    for (let i = 0; i < data.length; i++) data[i] = i % 2 ? 192 : 64;
    expect(rmsFromByteTimeDomain(data)).toBeCloseTo(0.5, 6);
  });
});

describe("rmsFromFloat32", () => {
  it("returns 0 for silence", () => {
    const data = new Float32Array(128).fill(0);
    expect(rmsFromFloat32(data)).toBeCloseTo(0, 6);
  });

  it("returns ~0.707 for a full-scale sine", () => {
    const data = new Float32Array(128);
    for (let i = 0; i < data.length; i++) data[i] = Math.sin((2 * Math.PI * i) / 8);
    expect(rmsFromFloat32(data)).toBeCloseTo(Math.SQRT1_2, 1);
  });
});

describe("BargeInDetector", () => {
  it("never fires on noise below threshold", () => {
    const d = new BargeInDetector({ threshold: 0.2, attackFrames: 3 });
    expect(d.feed(0.05)).toBe(false);
    expect(d.feed(0.1)).toBe(false);
    expect(d.feed(0.05)).toBe(false);
    expect(d.feed(0.1)).toBe(false);
    expect(d.feed(0.19)).toBe(false);
  });

  it("fires exactly once when sustained speech exceeds attack frames", () => {
    const d = new BargeInDetector({ threshold: 0.2, attackFrames: 3 });
    expect(d.feed(0.3)).toBe(false);
    expect(d.feed(0.3)).toBe(false);
    expect(d.feed(0.3)).toBe(true);
    expect(d.feed(0.3)).toBe(false);
    expect(d.feed(0.3)).toBe(false);
  });

  it("resets the attack counter on quiet frames", () => {
    const d = new BargeInDetector({ threshold: 0.2, attackFrames: 3 });
    expect(d.feed(0.3)).toBe(false);
    expect(d.feed(0.05)).toBe(false);
    expect(d.feed(0.3)).toBe(false);
    expect(d.feed(0.3)).toBe(false);
    expect(d.feed(0.3)).toBe(true);
  });

  it("reset() allows a new barge-in on the next turn", () => {
    const d = new BargeInDetector({ threshold: 0.2, attackFrames: 2 });
    d.feed(0.3);
    expect(d.feed(0.3)).toBe(true);
    d.reset();
    d.feed(0.3);
    expect(d.feed(0.3)).toBe(true);
  });

  it("uses VOICE_CONSTANTS defaults", () => {
    const d = new BargeInDetector();
    expect((d as unknown as { threshold: number }).threshold).toBe(
      VOICE_CONSTANTS.BARGE_IN_THRESHOLD
    );
    expect((d as unknown as { attackFrames: number }).attackFrames).toBe(
      VOICE_CONSTANTS.BARGE_IN_ATTACK_FRAMES
    );
    expect((d as unknown as { holdFrames: number }).holdFrames).toBe(0);
  });

  it("keeps the attack counter across short pauses (hold frames)", () => {
    const d = new BargeInDetector({ threshold: 0.2, attackFrames: 3, holdFrames: 2 });
    // loud, quiet (1 frame), loud, loud -> still fires despite one gap
    expect(d.feed(0.3)).toBe(false);
    expect(d.feed(0.05)).toBe(false);
    expect(d.feed(0.3)).toBe(false);
    expect(d.feed(0.3)).toBe(true);
  });

  it("resets the attack counter after too many quiet frames", () => {
    const d = new BargeInDetector({ threshold: 0.2, attackFrames: 3, holdFrames: 2 });
    d.feed(0.3);
    d.feed(0.05);
    d.feed(0.05);
    d.feed(0.05);
    d.feed(0.3);
    d.feed(0.3);
    expect(d.feed(0.3)).toBe(true);
  });

  it("arm() uses the higher no-AEC threshold when AEC is absent", () => {
    const d = new BargeInDetector();
    d.arm(false);
    const threshold = (d as unknown as { threshold: number }).threshold;
    expect(threshold).toBe(VOICE_CONSTANTS.BARGE_IN_NO_AEC_THRESHOLD);
    // a level above the AEC threshold but below the no-AEC threshold must NOT fire
    expect(d.feed(VOICE_CONSTANTS.BARGE_IN_NO_AEC_THRESHOLD - 0.01)).toBe(false);
  });

  it("arm() keeps the low threshold when AEC is present", () => {
    const d = new BargeInDetector();
    d.arm(true);
    expect((d as unknown as { threshold: number }).threshold).toBe(
      VOICE_CONSTANTS.BARGE_IN_THRESHOLD
    );
  });

  it("trackNoise raises the effective threshold above room noise", () => {
    const d = new BargeInDetector({ threshold: 0.06, attackFrames: 3 });
    // Ambient hum ~0.05 for a while
    for (let i = 0; i < 200; i++) d.trackNoise(0.05);
    const effective = d.effectiveThreshold;
    expect(effective).toBeGreaterThan(0.1);
    // a modest noise burst below the adaptive threshold does not fire
    expect(d.feed(0.09)).toBe(false);
    expect(d.feed(0.09)).toBe(false);
    // a real voice above it still fires within the attack window
    expect(d.feed(0.2)).toBe(false);
    expect(d.feed(0.2)).toBe(false);
    expect(d.feed(0.2)).toBe(true);
  });

  it("trackNoise ignores speech-like levels (never skews the floor up)", () => {
    const d = new BargeInDetector();
    d.trackNoise(0.5); // loud burst, must not be absorbed as noise
    d.trackNoise(0.5);
    const floor = (d as unknown as { noiseFloor: number }).noiseFloor;
    expect(floor).toBeLessThan(0.1);
  });

  it("effectiveThreshold never falls below the base threshold", () => {
    const d = new BargeInDetector({ threshold: 0.2 });
    d.trackNoise(0.004);
    expect(d.effectiveThreshold).toBeGreaterThanOrEqual(0.2);
  });
});
