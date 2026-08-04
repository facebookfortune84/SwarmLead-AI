export const COST_PER_LEAD_BASELINE = 68;
export const LEAD_ACQUISITION_DISCOUNT = 0.6;
export const PLATFORM_COST_PER_LEAD = 1.2;
export const DEFAULT_PLAN_COST_PER_MONTH = 99;

export interface ROIInput {
  leadsPerMonth: number;
  teamHours: number;
  hourlyRate?: number;
  planCostPerMonth?: number;
}

export interface ROIOutput {
  manualCost: number;
  leadCostSaved: number;
  automationCost: number;
  planCost: number;
  monthlySavings: number;
  yearlySavings: number;
  monthlySavingsFormatted: string;
  yearlySavingsFormatted: string;
  positive: boolean;
}

export function calculateROI({
  leadsPerMonth,
  teamHours,
  hourlyRate = 35,
  planCostPerMonth = DEFAULT_PLAN_COST_PER_MONTH,
}: ROIInput): ROIOutput {
  const manualCost = teamHours * hourlyRate;
  const leadCostSaved = leadsPerMonth * COST_PER_LEAD_BASELINE * LEAD_ACQUISITION_DISCOUNT;
  const automationCost = leadsPerMonth * PLATFORM_COST_PER_LEAD;
  const planCost = planCostPerMonth;
  const monthlySavings = manualCost + leadCostSaved - automationCost - planCost;
  const yearlySavings = monthlySavings * 12;

  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(Math.max(0, n));

  return {
    manualCost,
    leadCostSaved,
    automationCost,
    planCost,
    monthlySavings,
    yearlySavings,
    monthlySavingsFormatted: fmt(monthlySavings),
    yearlySavingsFormatted: fmt(yearlySavings),
    positive: monthlySavings > 0,
  };
}

export function clampLeads(value: number): number {
  if (!Number.isFinite(value)) return 200;
  return Math.min(5000, Math.max(10, Math.round(value)));
}

export function clampHours(value: number): number {
  if (!Number.isFinite(value)) return 80;
  return Math.min(400, Math.max(0, Math.round(value)));
}
