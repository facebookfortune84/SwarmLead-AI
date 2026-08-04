import { describe, it, expect } from "vitest";
import {
  calculateROI,
  clampHours,
  clampLeads,
  COST_PER_LEAD_BASELINE,
  LEAD_ACQUISITION_DISCOUNT,
  PLATFORM_COST_PER_LEAD,
} from "../roi";

describe("calculateROI", () => {
  it("computes manual labor cost from hours and rate", () => {
    const out = calculateROI({ leadsPerMonth: 200, teamHours: 80, hourlyRate: 35 });
    expect(out.manualCost).toBe(2800);
  });

  it("computes lead acquisition savings at the 60% discount", () => {
    const out = calculateROI({ leadsPerMonth: 200, teamHours: 80 });
    expect(out.leadCostSaved).toBe(200 * COST_PER_LEAD_BASELINE * LEAD_ACQUISITION_DISCOUNT);
  });

  it("computes automation cost at the flat per-lead platform price", () => {
    const out = calculateROI({ leadsPerMonth: 200, teamHours: 80 });
    expect(out.automationCost).toBe(200 * PLATFORM_COST_PER_LEAD);
  });

  it("subtracts the Genesis plan cost from savings", () => {
    const out = calculateROI({ leadsPerMonth: 200, teamHours: 80, planCostPerMonth: 99 });
    expect(out.planCost).toBe(99);
    expect(out.monthlySavings).toBe(2800 + 8160 - 240 - 99);
  });

  it("computes monthly and yearly savings", () => {
    const out = calculateROI({ leadsPerMonth: 200, teamHours: 80, hourlyRate: 35 });
    expect(out.monthlySavings).toBe(2800 + 8160 - 240 - 99);
    expect(out.yearlySavings).toBe(out.monthlySavings * 12);
  });

  it("marks savings as positive when automation beats manual cost", () => {
    expect(calculateROI({ leadsPerMonth: 500, teamHours: 80 }).positive).toBe(true);
  });

  it("marks savings as negative for tiny workloads", () => {
    const out = calculateROI({ leadsPerMonth: 1, teamHours: 0 });
    expect(out.positive).toBe(false);
  });

  it("never formats negative amounts below zero", () => {
    const out = calculateROI({ leadsPerMonth: 1, teamHours: 0 });
    expect(out.monthlySavingsFormatted).not.toContain("-");
    expect(out.yearlySavingsFormatted).not.toContain("-");
  });

  it("defaults the hourly rate to 35", () => {
    const withRate = calculateROI({ leadsPerMonth: 100, teamHours: 40, hourlyRate: 35 });
    const withoutRate = calculateROI({ leadsPerMonth: 100, teamHours: 40 });
    expect(withRate.manualCost).toBe(withoutRate.manualCost);
  });

  it("formats currency in USD with no decimals", () => {
    const out = calculateROI({ leadsPerMonth: 200, teamHours: 80 });
    expect(out.monthlySavingsFormatted).toMatch(/^\$[\d,]+$/);
    expect(out.yearlySavingsFormatted).toMatch(/^\$[\d,]+$/);
  });
});

describe("clampLeads", () => {
  it("clamps to the minimum of 10", () => {
    expect(clampLeads(1)).toBe(10);
    expect(clampLeads(-5)).toBe(10);
  });

  it("clamps to the maximum of 5000", () => {
    expect(clampLeads(99999)).toBe(5000);
  });

  it("rounds to integers", () => {
    expect(clampLeads(123.7)).toBe(124);
  });

  it("falls back to the default for NaN or Infinity", () => {
    expect(clampLeads(Number.NaN)).toBe(200);
    expect(clampLeads(Number.POSITIVE_INFINITY)).toBe(200);
  });
});

describe("clampHours", () => {
  it("clamps to the 0..400 range", () => {
    expect(clampHours(-10)).toBe(0);
    expect(clampHours(9999)).toBe(400);
  });

  it("rounds to integers", () => {
    expect(clampHours(45.6)).toBe(46);
  });

  it("falls back to the default for NaN", () => {
    expect(clampHours(Number.NaN)).toBe(80);
  });
});
