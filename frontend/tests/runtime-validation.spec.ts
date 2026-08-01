import { test, expect } from "@playwright/test";

test.describe("Runtime Validation", () => {

  test("Landing page renders and contains key elements", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("#main-content")).toBeVisible();
    await expect(page.locator("text=Voice AI is live").first()).toBeVisible();
  });

  test("Login page renders", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("body")).toBeVisible();
  });

  test("Dashboard page renders", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator("body")).toBeVisible();
  });

  test("Settings page renders", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.locator("body")).toBeVisible();
  });

  test("Billing page renders", async ({ page }) => {
    await page.goto("/billing");
    await expect(page.locator("body")).toBeVisible();
  });

  test("Backend health endpoint responds", async ({ page }) => {
    const response = await page.request.get("http://localhost:8000/health");
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.status).toBe("ok");
  });

  test("Backend ready endpoint responds", async ({ page }) => {
    const response = await page.request.get("http://localhost:8000/ready");
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.status).toBe("ready");
  });

  test("Backend OpenAPI has voice and webhook routes", async ({ page }) => {
    const response = await page.request.get("http://localhost:8000/openapi.json");
    expect(response.status()).toBe(200);
    const body = await response.json();
    const paths = Object.keys(body.paths);
    expect(paths).toContain("/api/voice/session");
    expect(paths).toContain("/api/stripe/webhook");
    expect(paths).toContain("/api/stripe/create-checkout-session");
  });

  test("Voice session creation endpoint responds", async ({ page }) => {
    const response = await page.request.post("http://localhost:8000/api/voice/session", {
      data: { greeting_type: "proactive" },
    });
    expect(response.ok()).toBeTruthy();
  });

});
