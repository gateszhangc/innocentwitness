const { test, expect } = require("@playwright/test");

test.describe("無垢なる証人 keyword site", () => {
  test("desktop homepage renders core sections, metadata, and faq interactions", async ({ page }) => {
    await page.goto("/");

    await expect(page).toHaveTitle(/無垢なる証人/);
    await expect(page.locator("h1")).toHaveText("無垢なる証人");
    await expect(page.locator('meta[name="description"]')).toHaveAttribute(
      "content",
      /2019年の韓国映画と2026年4月18日放送のテレビ朝日ドラマ版/
    );
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", "https://innocentwitness.lol/");

    await expect(page.getByText("このサイトは公式運営ではありません。")).toBeVisible();
    await expect(page.locator(".version-card")).toHaveCount(2);
    await expect(page.locator(".poster-card")).toHaveCount(2);
    await expect(page.getByRole("link", { name: "Klockworx 出典" })).toBeVisible();
    await expect(page.getByRole("link", { name: "テレビ朝日 出典" })).toBeVisible();
    await expect(page.locator('script[src*="googletagmanager.com"]')).toHaveCount(0);
    await expect(page.locator('script[src*="clarity.ms"]')).toHaveCount(0);

    const firstFaq = page.locator(".faq-list details").first();
    await firstFaq.locator("summary").click();
    await expect(firstFaq).toHaveAttribute("open", "");

    await expect(page.getByRole("link", { name: "テレビ朝日ドラマプレミアム『無垢なる証人』公式サイト" })).toBeVisible();
    await expect(page.locator(".footer-year")).toContainText(String(new Date().getFullYear()));

    const robotsResponse = await page.request.get("/robots.txt");
    expect(robotsResponse.ok()).toBe(true);
    await expect
      .soft(await robotsResponse.text())
      .toContain("Sitemap: https://innocentwitness.lol/sitemap.xml");

    const sitemapResponse = await page.request.get("/sitemap.xml");
    expect(sitemapResponse.ok()).toBe(true);
    await expect.soft(await sitemapResponse.text()).toContain("<loc>https://innocentwitness.lol/</loc>");

    const imagesLoaded = await page.evaluate(() =>
      Array.from(document.images).every((image) => image.complete && image.naturalWidth > 0)
    );
    expect(imagesLoaded).toBe(true);
  });

  test("mobile layout stays within viewport and keeps version section accessible", async ({ browser }) => {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true
    });
    const page = await context.newPage();

    await page.goto("/");
    await expect(page.locator("h1")).toBeVisible();
    await page.getByRole("link", { name: "作品比較を見る" }).click();
    await expect(page.locator("#versions")).toBeInViewport();

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(1);

    await expect(page.locator(".version-card")).toHaveCount(2);
    await expect(page.locator(".cast-column")).toHaveCount(2);
    await context.close();
  });
});
