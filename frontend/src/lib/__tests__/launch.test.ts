import { describe, it, expect } from "vitest";
import { recommendPlan, shareUrl, PRODUCT_HUNT_URL, LAUNCH_COPY } from "../launch";

describe("recommendPlan", () => {
  it("recommends starter for solo founders on a budget", () => {
    expect(
      recommendPlan({ goal: "launch", teamSize: "solo", budget: "free" })
    ).toBe("starter");
  });

  it("recommends growth for small teams with mid budget", () => {
    expect(
      recommendPlan({ goal: "scale", teamSize: "small", budget: "mid" })
    ).toBe("growth");
  });

  it("recommends enterprise for large teams with premium budget", () => {
    expect(
      recommendPlan({ goal: "automate", teamSize: "large", budget: "premium" })
    ).toBe("enterprise");
  });

  it("scores automate-heavy solo founders into growth", () => {
    expect(
      recommendPlan({ goal: "automate", teamSize: "solo", budget: "mid" })
    ).toBe("growth");
  });
});

describe("shareUrl", () => {
  it("builds an x share link containing the product hunt url", () => {
    const url = shareUrl("x");
    expect(url).toContain("twitter.com/intent/tweet");
    expect(decodeURIComponent(url)).toContain(PRODUCT_HUNT_URL);
  });

  it("builds facebook / linkedin / whatsapp / email links", () => {
    expect(shareUrl("facebook")).toContain("facebook.com/sharer");
    expect(shareUrl("linkedin")).toContain("linkedin.com/sharing");
    expect(shareUrl("whatsapp")).toContain("wa.me");
    expect(shareUrl("email")).toContain("mailto:");
  });
});

describe("launch copy", () => {
  it("exposes the promo code and offer", () => {
    expect(LAUNCH_COPY.promoCode).toBe("LAUNCH100");
    expect(LAUNCH_COPY.promoOffer).toContain("month free");
  });
});
