import { test, expect, type Page, type APIRequestContext } from "@playwright/test";

const LOGIN_EMAIL = "verify@realms2riches.com";
const LOGIN_PASSWORD = "VerifyTest123!";

async function getTokens(request: APIRequestContext) {
  const res = await request.post("/api/auth/login", {
    data: { email: LOGIN_EMAIL, password: LOGIN_PASSWORD },
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  return {
    access: body.access_token,
    refresh: body.refresh_token,
  };
}

async function seedAuth(page: Page, access: string, refresh: string) {
  await page.addInitScript(
    ([accessToken, refreshToken]) => {
      localStorage.setItem("swarmlead_access_token", accessToken);
      localStorage.setItem("swarmlead_refresh_token", refreshToken);
    },
    [access, refresh]
  );
}

test.describe("Public landing page", () => {
  test("renders premium marketing sections", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("text=Frequently Asked Questions").first()).toBeVisible();
    await expect(page.locator("text=Get Started").first()).toBeVisible();
    await expect(page.locator("h1").first()).toBeVisible();
    const body = await page.locator("body").innerText();
    expect(body.length).toBeGreaterThan(3000);
  });
});

test.describe("Authenticated app UI", () => {
  let tokens: { access: string; refresh: string };

  test.beforeAll(async ({ request }) => {
    tokens = await getTokens(request);
  });

  test("dashboard shows Company Builder", async ({ page }) => {
    await seedAuth(page, tokens.access, tokens.refresh);
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("button", { name: /Build My Company/i })).toBeVisible();
    await expect(page.locator("text=Company Builder").first()).toBeVisible();
  });

  test("workflows page shows template gallery and Tenant ID input", async ({ page }) => {
    await seedAuth(page, tokens.access, tokens.refresh);
    await page.goto("/workflows");
    await page.waitForLoadState("networkidle");

    await expect(page.getByPlaceholder("TEN-57253941", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: /Use Template/i }).first()).toBeVisible();
    await expect(page.locator("text=Email Follow-Up").first()).toBeVisible();
  });

  test("tickets page shows New Ticket button and lead picker", async ({ page }) => {
    await seedAuth(page, tokens.access, tokens.refresh);
    await page.goto("/tickets");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("button", { name: /New Ticket/i })).toBeVisible();
    await expect(page.locator("select").first()).toBeVisible();
  });
});
