import { test, expect } from "@playwright/test";

const FRONTEND = "http://localhost:3000";
const BACKEND = "http://localhost:8000";

test.describe("Premium Frontend Validation", () => {

  test("Landing page has premium HeroSection with title and CTA", async ({ page }) => {
    await page.goto(FRONTEND);
    await expect(page.locator("h1")).toContainText("Launch your business");
    await expect(page.getByRole("link", { name: /start free/i }).first()).toBeVisible();
    await expect(page.getByRole("link", { name: /watch demo/i }).first()).toBeVisible();
    await expect(page.locator("text=Voice AI is live")).toBeVisible();
  });

  test("VoiceLandingAgent is present on landing", async ({ page }) => {
    await page.goto(FRONTEND);
    const voiceAgentImg = page.locator('img[alt="Genesis AI Voice Agent"]');
    const voiceOrb = page.locator("[data-testid='voice-orb']");
    const either = voiceAgentImg.or(voiceOrb);
    await expect(either).toBeVisible();
  });

  test("FeatureShowcase renders premium features", async ({ page }) => {
    await page.goto(FRONTEND);
    await expect(page.getByRole("heading", { name: /voice-first/i }).first()).toBeVisible();
  });

  test("Dashboard page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`);
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1, h2").first()).toBeVisible();
  });

  test("Onboarding page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/onboarding`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("Billing page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/billing`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("Settings page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/settings`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("Profile page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/profile`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("Leads page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/leads`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("Tenants page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/tenants`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("Workflows page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/workflows`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("Tickets page redirects to login when unauthenticated", async ({ page }) => {
    test.skip(true, "Client-side redirect requires auth context");
  });

  test("Agents page renders", async ({ page }) => {
    await page.goto(`${FRONTEND}/agents`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("All premium page routes respond via fetch", async ({ page }) => {
    const routes = ["/", "/dashboard", "/onboarding", "/billing", "/settings", "/profile", "/leads", "/tenants", "/workflows", "/tickets", "/agents", "/login", "/notifications", "/outreach", "/demo", "/cancel", "/success"];
    for (const route of routes) {
      const resp = await page.request.get(`${FRONTEND}${route}`);
      expect(resp.status(), `${route} returned ${resp.status()}`).toBe(200);
    }
  });

  test.skip("Sidebar navigation renders with all premium links", async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`);
    const sidebarLinks = ["Dashboard", "Leads", "Tickets", "Workflows", "Voice", "Outreach", "Settings"];
    for (const link of sidebarLinks) {
      await expect(page.locator(`text=${link}`).first()).toBeVisible();
    }
  });

  test("Backend API health is OK", async ({ page }) => {
    const resp = await page.request.get(`${BACKEND}/health`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("ok");
  });

  test("Backend API has all premium routes", async ({ page }) => {
    const resp = await page.request.get(`${BACKEND}/openapi.json`);
    const body = await resp.json();
    const paths = Object.keys(body.paths);
    const required = ["/api/voice/session", "/api/stripe/webhook", "/api/stripe/create-checkout-session", "/api/auth/login", "/api/auth/register", "/api/leads", "/api/workflows"];
    for (const route of required) {
      expect(paths, `Missing route: ${route}`).toContain(route);
    }
  });

  test("Voice session creation works against live API", async ({ page }) => {
    const resp = await page.request.post(`${BACKEND}/api/voice/session`, {
      data: { greeting_type: "proactive" },
    });
    expect(resp.ok()).toBeTruthy();
  });

  test("Landing page HTML contains premium content", async ({ page }) => {
    await page.goto(FRONTEND);
    const html = await page.content();
    expect(html).toContain("Genesis");
    expect(html).toContain("Voice");
    expect(html).toContain("main-content");
    expect(html).toContain("Launch your business");
    expect(html).toContain("Start Free");
  });

});
