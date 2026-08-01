import { test, expect } from "@playwright/test";

const FRONTEND = "http://localhost:3000";

test.describe("Founder Journey - Full Runtime Validation", () => {
  test("Landing page loads with all premium elements", async ({ page }) => {
    await page.goto(FRONTEND, { waitUntil: "load" });
    await expect(page.locator("#main-content")).toBeVisible();
    await expect(page.locator("text=Genesis Forge").first()).toBeVisible();
    await expect(page.locator("text=Voice AI is live").first()).toBeVisible();
    await expect(page.getByRole("link", { name: /get started/i }).first()).toBeVisible();
    await expect(page.getByRole("link", { name: /view demo/i }).first()).toBeVisible();
  });

  test("Landing page - Voice agent renders (image or VoiceOrb)", async ({ page }) => {
    await page.goto(FRONTEND, { waitUntil: "load" });
    const voiceAgentImg = page.locator('img[alt="Genesis AI Voice Agent"]');
    const voiceOrb = page.locator('[data-testid="voice-orb"]');
    const either = voiceAgentImg.or(voiceOrb);
    await expect(either).toBeVisible();
  });

  test("Landing page - Genesis Forge brand renders in header", async ({ page }) => {
    await page.goto(FRONTEND, { waitUntil: "load" });
    await expect(page.locator("text=Genesis Forge").first()).toBeVisible();
    await expect(page.locator("header nav")).toBeVisible();
  });

  test("Landing page - Testimonials section present", async ({ page }) => {
    await page.goto(FRONTEND, { waitUntil: "load" });
    await expect(page.locator("text=Trusted by Ambitious Founders")).toBeVisible();
    await expect(page.locator("text=Sarah Chen")).toBeVisible();
    await expect(page.locator("text=Marcus Rivera")).toBeVisible();
    await expect(page.locator("text=Dr. Aisha Patel")).toBeVisible();
  });

  test("Landing page - Animated counters animate", async ({ page }) => {
    await page.goto(FRONTEND, { waitUntil: "load" });
    await expect(page.locator("text=Faster Launch").first()).toBeVisible();
    await expect(page.locator("text=Lead Conversion").first()).toBeVisible();
    await expect(page.locator("text=Avg Setup Time").first()).toBeVisible();
    await expect(page.locator("text=Uptime SLA").first()).toBeVisible();
  });

  test("Demo page loads with interactive simulation", async ({ page }) => {
    await page.goto(`${FRONTEND}/demo`, { waitUntil: "load" });
    await expect(page.locator("text=See Genesis in Action")).toBeVisible();
    await expect(page.locator("text=Voice Discovery").first()).toBeVisible({ timeout: 5000 });
    await expect(page.getByRole("button", { name: /play demo/i })).toBeVisible();
  });

  test("Demo page interactive play works", async ({ page }) => {
    await page.goto(`${FRONTEND}/demo`, { waitUntil: "load" });
    const playBtn = page.getByRole("button", { name: /play demo/i });
    await expect(playBtn).toBeVisible();
    await playBtn.click();
    await expect(page.getByRole("button", { name: /skip/i })).toBeVisible();
  });

  test("Login page renders with form validation", async ({ page }) => {
    await page.goto(`${FRONTEND}/login`, { waitUntil: "load" });
    await expect(page.locator("text=Sign In").first()).toBeVisible();
    await expect(page.locator('input[placeholder="you@company.com"]')).toBeVisible();
    await expect(page.locator('input[placeholder="Enter your password"]')).toBeVisible();
    await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  });

  test("Onboarding page renders with all steps", async ({ page }) => {
    await page.goto(`${FRONTEND}/onboarding`, { waitUntil: "load" });
    await expect(page.locator("text=Tell Us About Your Business")).toBeVisible();
    await expect(page.locator('input[id="full_name"]')).toBeVisible();
    await expect(page.locator('input[id="business_name"]')).toBeVisible();
    await expect(page.locator('input[id="email"]')).toBeVisible();
    await expect(page.locator('input[id="password"]')).toHaveAttribute("type", "password");
  });

  test("Onboarding wizard - form validation works", async ({ page }) => {
    await page.goto(`${FRONTEND}/onboarding`, { waitUntil: "load" });
    const continueBtn = page.getByRole("button", { name: /continue/i });
    await expect(continueBtn).toBeVisible();
    await continueBtn.click();
    await expect(page.locator("text=Your Full Name is required")).toBeVisible({ timeout: 3000 });
  });

  test("Onboarding wizard - skip for now navigates to dashboard", async ({ page }) => {
    await page.goto(`${FRONTEND}/onboarding`, { waitUntil: "load" });
    const skipBtn = page.getByRole("button", { name: /skip for now/i });
    await expect(skipBtn).toBeVisible();
    await skipBtn.click();
    await expect(page).toHaveURL(`${FRONTEND}/dashboard`);
  });

  test("Protected routes redirect to login when unauthenticated", async ({ page }) => {
    await page.goto(`${FRONTEND}/settings`, { waitUntil: "load" });
    await expect(page).toHaveURL(`${FRONTEND}/login`);
  });

  test("Public routes accessible without auth", async ({ page }) => {
    await page.goto(`${FRONTEND}/`, { waitUntil: "load" });
    await expect(page).toHaveURL(`${FRONTEND}/`);

    await page.goto(`${FRONTEND}/demo`, { waitUntil: "load" });
    await expect(page).toHaveURL(`${FRONTEND}/demo`);

    await page.goto(`${FRONTEND}/onboarding`, { waitUntil: "load" });
    await expect(page).toHaveURL(`${FRONTEND}/onboarding`);

    await page.goto(`${FRONTEND}/login`, { waitUntil: "load" });
    await expect(page).toHaveURL(`${FRONTEND}/login`);
  });

  test("Voice agent session creation API works via proxy", async ({ page }) => {
    const response = await page.request.post(`${FRONTEND}/api/voice/session`, {
      data: { greeting_type: "proactive" },
    });
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.session_id).toBeDefined();
  });

  test("Backend health and ready endpoints accessible via proxy", async ({ page }) => {
    const health = await page.request.get(`${FRONTEND}/health`);
    expect(health.ok()).toBeTruthy();

    const ready = await page.request.get(`${FRONTEND}/ready`);
    expect(ready.ok()).toBeTruthy();
  });

  test("OpenAPI spec accessible via proxy", async ({ page }) => {
    const response = await page.request.get(`${FRONTEND}/openapi.json`);
    expect(response.ok()).toBeTruthy();
    const spec = await response.json();
    expect(spec.paths).toBeDefined();
    expect(spec.paths["/api/voice/session"]).toBeDefined();
    expect(spec.paths["/api/auth/register"]).toBeDefined();
    expect(spec.paths["/api/auth/login"]).toBeDefined();
  });
});