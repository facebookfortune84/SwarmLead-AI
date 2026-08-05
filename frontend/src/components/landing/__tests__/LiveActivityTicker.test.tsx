// @vitest-environment jsdom
import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, cleanup, act } from "@testing-library/react";
import { LiveActivityTicker } from "../LiveActivityTicker";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

function mockFetch(body: unknown) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(body),
    })
  );
}

const SAMPLE_ACTIVITY = {
  launch_week: true,
  leads_since_launch: 42,
  leads_by_source: { voice: 30, plan_quiz: 12 },
  high_intent_leads: 17,
  growth_cycles: 9,
  approval_pending: 3,
};

describe("LiveActivityTicker", () => {
  it("renders real activity moments when the API responds", async () => {
    mockFetch(SAMPLE_ACTIVITY);
    await act(async () => {
      render(<LiveActivityTicker />);
      await Promise.resolve();
    });
    expect(screen.getAllByText(/Launch week is live — 42 leads captured so far/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/17 high-intent leads waiting in your queue/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Most leads coming from the voice agent — 30/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/9 growth cycles run since launch/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/3 actions awaiting your approval/i).length).toBeGreaterThan(0);
  });

  it("falls back to honest feature copy when the API fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    await act(async () => {
      render(<LiveActivityTicker />);
      await Promise.resolve();
    });
    // Neutral capability copy — never fabricated live testimonials.
    expect(screen.getAllByText(/15 agents run outreach, SEO.*behind one approval gate/i).length).toBeGreaterThan(0);
  });

  it("links to the Product Hunt upvote page", async () => {
    mockFetch({ ...SAMPLE_ACTIVITY, leads_since_launch: 0, high_intent_leads: 0 });
    await act(async () => {
      render(<LiveActivityTicker />);
      await Promise.resolve();
    });
    const link = screen.getByRole("link", { name: /Upvote Genesis Forge on Product Hunt/i });
    expect(link.getAttribute("href")).toContain("producthunt.com/products/genesis-5");
    expect(link.getAttribute("target")).toBe("_blank");
    expect(link.getAttribute("rel")).toContain("noopener");
  });
});
