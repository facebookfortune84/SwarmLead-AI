import { PUBLIC_DOMAIN, shareLink } from "./site";

export const PRODUCT_HUNT_URL =
  "https://www.producthunt.com/products/genesis-5?utm_source=" +
  encodeURIComponent(PUBLIC_DOMAIN) +
  "&utm_medium=social";

export const LAUNCH_COPY = {
  promoCode: "LAUNCH100",
  promoOffer: "1 month free on any plan",
  referralCredit: "$50 credit",
  referralDiscount: "20% off first month",
};

const SHARE_TEXT =
  "Launch your business with your voice. Genesis Forge is live on Product Hunt — 19 AI agents run your whole operation behind one human approval gate.";

export function shareUrl(network: "x" | "facebook" | "linkedin" | "whatsapp" | "email"): string {
  return shareLink(network, PRODUCT_HUNT_URL, SHARE_TEXT);
}

export interface PlanQuizAnswer {
  goal: "launch" | "scale" | "automate";
  teamSize: "solo" | "small" | "large";
  budget: "free" | "mid" | "premium";
}

export function recommendPlan(answers: PlanQuizAnswer): "starter" | "growth" | "enterprise" {
  const { teamSize, budget, goal } = answers;
  let score = 0;
  if (teamSize === "small") score += 1;
  if (teamSize === "large") score += 2;
  if (budget === "mid") score += 1;
  if (budget === "premium") score += 2;
  if (goal === "scale") score += 1;
  if (goal === "automate") score += 2;
  if (score >= 4) return "enterprise";
  if (score >= 2) return "growth";
  return "starter";
}
