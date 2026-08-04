// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { act, render, screen, cleanup } from "@testing-library/react";
import { ProductHuntCountdown } from "../ProductHuntCountdown";
import { PRODUCT_HUNT_LAUNCH_AT } from "@/lib/countdown";

const launchTimestamp = PRODUCT_HUNT_LAUNCH_AT.getTime();

describe("ProductHuntCountdown", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(launchTimestamp + 60_000);
  });

  afterEach(() => {
    vi.useRealTimers();
    cleanup();
  });

  it("renders the live state after the launch moment", () => {
    render(<ProductHuntCountdown />);
    expect(screen.getByText(/We are LIVE on Product Hunt/i)).toBeTruthy();
    expect(screen.getByText(/Genesis Forge is launching right now/i)).toBeTruthy();
  });

  it("links the live CTA to the Genesis 5 Product Hunt page", () => {
    render(<ProductHuntCountdown />);
    const link = screen.getByRole("link", { name: /Upvote on Product Hunt/i });
    expect(link.getAttribute("href")).toContain("producthunt.com/products/genesis-5");
    expect(link.getAttribute("target")).toBe("_blank");
    expect(link.getAttribute("rel")).toContain("noopener");
  });

  it("renders ticking time units before the launch moment", () => {
    vi.setSystemTime(launchTimestamp - 3 * 86_400_000 - 4_200_000 - 60_000);
    render(<ProductHuntCountdown />);
    expect(screen.getByText(/Days/i)).toBeTruthy();
    expect(screen.getByText(/Hours/i)).toBeTruthy();
    expect(screen.getByText(/Minutes/i)).toBeTruthy();
    expect(screen.getByText(/Seconds/i)).toBeTruthy();
    expect(screen.getByText(/1 month free/i)).toBeTruthy();
  });

  it("ticks every second while waiting for launch", () => {
    vi.setSystemTime(launchTimestamp - 2000);
    render(<ProductHuntCountdown />);
    expect(screen.getByText("02")).toBeTruthy();
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.getByText("01")).toBeTruthy();
  });
});
