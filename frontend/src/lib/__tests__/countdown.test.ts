import { describe, it, expect } from "vitest";
import {
  formatTargetLabel,
  getTimeLeft,
  pad,
  PRODUCT_HUNT_LAUNCH_AT,
} from "../countdown";

describe("getTimeLeft", () => {
  it("returns all-zero + live=true when the target has passed", () => {
    const after = new Date("2026-08-05T00:00:00Z").getTime();
    expect(getTimeLeft(new Date("2026-08-03T00:01:00-04:00"), after)).toEqual({
      days: 0,
      hours: 0,
      minutes: 0,
      seconds: 0,
      live: true,
    });
  });

  it("returns live=true exactly at the target", () => {
    const target = new Date("2026-08-03T00:01:00-04:00").getTime();
    expect(getTimeLeft(new Date("2026-08-03T00:01:00-04:00"), target).live).toBe(true);
  });

  it("splits remaining time into days, hours, minutes, seconds", () => {
    const target = new Date("2026-08-10T00:00:00Z").getTime();
    const now = new Date("2026-08-03T00:00:00Z").getTime();
    const left = getTimeLeft(new Date(target), now);
    expect(left.live).toBe(false);
    expect(left.days).toBe(7);
    expect(left.hours).toBe(0);
    expect(left.minutes).toBe(0);
    expect(left.seconds).toBe(0);
  });

  it("handles sub-minute offsets correctly", () => {
    const target = new Date("2026-08-03T00:10:00Z").getTime();
    const now = new Date("2026-08-03T00:07:42Z").getTime();
    const left = getTimeLeft(new Date(target), now);
    expect(left.minutes).toBe(2);
    expect(left.seconds).toBe(18);
  });

  it("never produces negative components", () => {
    const target = new Date("2026-08-03T00:01:00-04:00").getTime();
    const now = target + 5000;
    const left = getTimeLeft(new Date("2026-08-03T00:01:00-04:00"), now);
    expect(left.days).toBeGreaterThanOrEqual(0);
    expect(left.hours).toBeGreaterThanOrEqual(0);
    expect(left.minutes).toBeGreaterThanOrEqual(0);
    expect(left.seconds).toBeGreaterThanOrEqual(0);
  });
});

describe("pad", () => {
  it("left-pads single digits with a zero", () => {
    expect(pad(0)).toBe("00");
    expect(pad(5)).toBe("05");
  });

  it("passes through two-digit values unchanged", () => {
    expect(pad(42)).toBe("42");
  });

  it("handles values above 99", () => {
    expect(pad(100)).toBe("100");
  });
});

describe("formatTargetLabel", () => {
  it("formats the launch moment in en-US with a weekday", () => {
    const label = formatTargetLabel(PRODUCT_HUNT_LAUNCH_AT);
    expect(label).toMatch(/Monday, August 3/);
  });
});

describe("PRODUCT_HUNT_LAUNCH_AT", () => {
  it("is the Product Hunt launch moment: 2026-08-03 00:01 EDT", () => {
    expect(PRODUCT_HUNT_LAUNCH_AT.getFullYear()).toBe(2026);
    expect(PRODUCT_HUNT_LAUNCH_AT.getMonth()).toBe(7); // August
    expect(PRODUCT_HUNT_LAUNCH_AT.getDate()).toBe(3);
  });
});
