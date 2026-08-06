import { describe, it, expect } from "vitest";
import {
  formatCents,
  formatCentsCents,
  annualPrice,
  annualSavings,
  stageLabel,
  percent,
  compactMoney,
} from "@/lib/money";

describe("formatCents", () => {
  it("formats integer dollars from cents", () => {
    expect(formatCents(9900)).toBe("$99");
    expect(formatCents(2900)).toBe("$29");
  });

  it("handles zero and undefined", () => {
    expect(formatCents(0)).toBe("$0");
    expect(formatCents(null)).toBe("$0");
    expect(formatCents(undefined)).toBe("$0");
  });
});

describe("formatCentsCents", () => {
  it("keeps the cents fraction", () => {
    expect(formatCentsCents(99000)).toBe("$990.00");
  });
});

describe("annual pricing", () => {
  it("charges 10x monthly for a year (2 months free)", () => {
    expect(annualPrice(99)).toBe(990);
  });

  it("savings equal two months", () => {
    expect(annualSavings(99)).toBe(198);
    expect(annualSavings(29)).toBe(58);
  });

  it("honors a custom multiplier", () => {
    expect(annualPrice(99, 11)).toBe(1089);
    expect(annualSavings(99, 11)).toBe(99);
  });
});

describe("stageLabel", () => {
  it("title-cases snake_case stages", () => {
    expect(stageLabel("closed_won")).toBe("Closed Won");
    expect(stageLabel("qualified")).toBe("Qualified");
  });
});

describe("percent", () => {
  it("converts a ratio to an integer percentage", () => {
    expect(percent(0.15)).toBe("15%");
    expect(percent(1)).toBe("100%");
  });
});

describe("compactMoney", () => {
  it("compresses thousands to k", () => {
    expect(compactMoney(1200)).toBe("$1k");
    expect(compactMoney(250)).toBe("$250");
  });
});