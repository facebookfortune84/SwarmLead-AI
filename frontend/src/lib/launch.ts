export const PRODUCT_HUNT_URL =
  "https://www.producthunt.com/products/genesis-5?utm_source=realms2riches.com&utm_medium=social";

export const SITE_URL = "https://realms2riches.com";

export const LAUNCH_COPY = {
  promoCode: "LAUNCH100",
  promoOffer: "1 month free on any plan",
  referralCredit: "$50 credit",
  referralDiscount: "20% off first month",
};

const SHARE_TEXT =
  "Launch your business with your voice. Genesis Forge is live on Product Hunt — 15 AI agents run your whole operation behind one human approval gate.";

export function shareUrl(network: "x" | "facebook" | "linkedin" | "whatsapp" | "email"): string {
  const text = encodeURIComponent(SHARE_TEXT);
  const url = encodeURIComponent(PRODUCT_HUNT_URL);
  switch (network) {
    case "x":
      return `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
    case "facebook":
      return `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    case "linkedin":
      return `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
    case "whatsapp":
      return `https://wa.me/?text=${text}%20${url}`;
    case "email":
      return `mailto:?subject=${encodeURIComponent("Launch your business with your voice")}&body=${text}%20${url}`;
  }
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
