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
  });
});
