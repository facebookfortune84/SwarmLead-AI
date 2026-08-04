export const PRODUCT_HUNT_LAUNCH_AT = new Date("2026-08-03T00:01:00-04:00");

export interface TimeLeft {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  live: boolean;
}

export function getTimeLeft(target: Date, now: number = Date.now()): TimeLeft {
  const diff = target.getTime() - now;
  if (diff <= 0) return { days: 0, hours: 0, minutes: 0, seconds: 0, live: true };
  const totalSeconds = Math.floor(diff / 1000);
  return {
    days: Math.floor(totalSeconds / 86400),
    hours: Math.floor((totalSeconds % 86400) / 3600),
    minutes: Math.floor((totalSeconds % 3600) / 60),
    seconds: totalSeconds % 60,
    live: false,
  };
}

export function pad(value: number): string {
  return String(value).padStart(2, "0");
}

export function formatTargetLabel(target: Date): string {
  return target.toLocaleString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}
