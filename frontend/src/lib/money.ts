/** Money + revenue formatting helpers (pure, unit-testable). */

export function formatCents(cents: number | null | undefined): string {
  const value = Math.round((cents ?? 0) / 100);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatCentsCents(cents: number | null | undefined): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format((cents ?? 0) / 100);
}

/** Annual price (2 months free) from a monthly amount in dollars. */
export function annualPrice(monthlyUsd: number, multiplier = 10): number {
  return monthlyUsd * multiplier;
}

/** Savings of going annual vs paying monthly for the year, in dollars. */
export function annualSavings(monthlyUsd: number, multiplier = 10): number {
  return monthlyUsd * 12 - annualPrice(monthlyUsd, multiplier);
}

/** Human stage label ('closed_won' -> 'Closed won'). */
export function stageLabel(stage: string): string {
  return stage
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Percent 0..1 -> "15%". */
export function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

/** Short dollar value: 99000 -> "$99k/yr" style helpers. */
export function compactMoney(dollars: number): string {
  if (dollars >= 1000) {
    return `$${Math.round(dollars / 1000)}k`;
  }
  return `$${Math.round(dollars)}`;
}