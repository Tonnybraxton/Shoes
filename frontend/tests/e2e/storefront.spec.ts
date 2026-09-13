import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('soleline:consent', 'essential'));
});

test('card colorway switches image and price without navigating or shifting layout', async ({
  page,
}) => {
  await page.goto('/shop');
  const card = page.getByTestId('product-card').first();
  await expect(card).toBeVisible();
  const img = card.locator('.product-image'),
    old = await img.getAttribute('src'),
    price = await card.locator('.price').textContent(),
    bounds = await card.boundingBox(),
    url = page.url();
  const swatches = card.getByRole('button', { name: /Select .* colorway/ });
  await swatches.nth(1).click();
  await expect(img).not.toHaveAttribute('src', old!);
  await expect(card.locator('.price')).not.toHaveText(price!);
  expect(page.url()).toBe(url);
  const after = await card.boundingBox();
  expect(Math.abs(after!.height - bounds!.height)).toBeLessThanOrEqual(1);
  await expect(swatches.nth(1)).toHaveAttribute('aria-pressed', 'true');
});
test('extra swatches expand accessibly', async ({ page }) => {
  await page.goto('/shop');
  const card = page.getByTestId('product-card').first();
  await card.getByRole('button', { name: /Show .* more colorways/ }).click();
  await expect(card.getByRole('button', { name: /Select .* colorway/ })).toHaveCount(5);
});
test('PDP requires size, adds exact variant and bag reprices quantity', async ({ page }) => {
  await page.goto('/products/velocity-02');
  await page.getByRole('button', { name: 'Add to bag', exact: true }).click();
  await expect(
    page.getByText('Choose a size before adding this pair.', { exact: true }),
  ).toBeVisible();
  await page
    .locator('.pdp-colors')
    .getByRole('button', { name: 'Select Graphite / Silver colorway' })
    .click();
  await page.getByRole('button', { name: 'Size EU 42', exact: true }).click();
  await page.getByRole('button', { name: 'Add to bag', exact: true }).click();
  await expect(page.getByRole('status')).toContainText('Added to your bag');
  await page.goto('/cart');
  await expect(page.getByText('Graphite / Silver', { exact: true })).toBeVisible();
  await expect(page.getByText('Size EU 42', { exact: true })).toBeVisible();
  const total = page.locator('.summary-row.total');
  const before = await total.innerText();
  await page.getByRole('button', { name: 'Increase Velocity 02 quantity' }).click();
  await expect(total).not.toHaveText(before);
  await page.screenshot({ path: '../docs/screenshots/cart-desktop.png', fullPage: true });
});
test('out of stock exact size opens restock instead of allowing purchase', async ({ page }) => {
  await page.goto('/products/velocity-02');
  const size = page.getByRole('button', { name: 'Size EU 36, out of stock, request notification' });
  await expect(size).toHaveAttribute('aria-disabled', 'true');
  await size.click({ force: true });
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('dialog')).toContainText('EU 36');
});
test('combined filters survive refresh and sort changes', async ({ page }) => {
  await page.goto('/shop');
  await page.getByRole('checkbox', { name: /^ARC/ }).first().check();
  await page.getByRole('button', { name: '42', exact: true }).first().click();
  await page.getByLabel('Sort products').selectOption('price_desc');
  await expect(page).toHaveURL(/brand=arc/);
  await expect(page).toHaveURL(/size=42/);
  await expect(page).toHaveURL(/sort=price_desc/);
  await page.reload();
  await expect(page.getByLabel('Sort products')).toHaveValue('price_desc');
  await expect(page.getByTestId('product-card')).toHaveCount(3);
});
test('search autocomplete works with keyboard selection and Escape', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Search the store' }).click();
  const search = page.getByRole('combobox');
  await search.fill('Velocity');
  await expect(page.getByRole('option').first()).toBeVisible();
  await search.press('ArrowDown');
  await search.press('Enter');
  await expect(page).toHaveURL(/\/products\/velocity/);
  await page.getByRole('button', { name: 'Search the store' }).click();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).not.toBeVisible();
});
test('guest wishlist persists after refresh', async ({ page }) => {
  await page.goto('/shop');
  await page.getByRole('button', { name: 'Save Velocity 02 to wishlist' }).click();
  await page.goto('/wishlist');
  await expect(page.getByTestId('product-card')).toHaveCount(1);
  await page.reload();
  await expect(page.getByText('Velocity 02', { exact: true })).toBeVisible();
});
test('compare shows real catalogue fields', async ({ page }) => {
  await page.goto('/shop');
  await page
    .getByTestId('product-card')
    .nth(0)
    .getByRole('button', { name: 'Compare', exact: true })
    .click();
  await page
    .getByTestId('product-card')
    .nth(1)
    .getByRole('button', { name: 'Compare', exact: true })
    .click();
  await page.getByRole('link', { name: /Compare your pairs 2/ }).click();
  await expect(page.getByRole('table')).toContainText('Velocity 02');
  await expect(page.getByRole('table')).toContainText('Court Theory');
});
test('guest development checkout creates a verified test order', async ({ page }) => {
  await page.goto('/products/terrain-one');
  await page.getByRole('button', { name: 'Size EU 44', exact: true }).click();
  await page.getByRole('button', { name: 'Add to bag', exact: true }).click();
  await expect(page.getByRole('status')).toContainText('Added to your bag');
  await page.goto('/checkout');
  await page.getByLabel('First name', { exact: true }).fill('Test');
  await page.getByLabel('Last name', { exact: true }).fill('Shopper');
  await page.getByLabel('Email address', { exact: true }).fill(`guest-${Date.now()}@example.test`);
  await page.getByLabel('Phone number', { exact: true }).fill('+254700000000');
  await page.getByLabel('Street address', { exact: true }).fill('1 Test Lane');
  await page.getByLabel('City / town', { exact: true }).fill('Nairobi');
  await page.getByLabel('County', { exact: true }).fill('Nairobi');
  await page.getByRole('checkbox').check();
  await page.screenshot({ path: '../docs/screenshots/checkout-desktop.png', fullPage: true });
  await page.getByRole('button', { name: 'Place demonstration order' }).click();
  await expect(page).toHaveURL(/\/orders\//);
  await expect(page.getByRole('heading', { name: 'Your next move is in.' })).toBeVisible();
  await page.screenshot({ path: '../docs/screenshots/order-confirmation.png', fullPage: true });
});
test('registration profile and logout work through session cookies', async ({ page }) => {
  const email = `account-${Date.now()}@example.test`;
  const password = 'rotation!september-2026-X';
  await page.goto('/account');
  await page.getByRole('button', { name: 'New here? Create an account' }).click();
  await page.getByLabel('First name').fill('Demo');
  await page.getByLabel('Last name').fill('Member');
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Create account', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Your space, Demo.' })).toBeVisible();
  await page.getByLabel('First name').fill('Updated');
  await page.getByRole('button', { name: 'Save changes' }).click();
  await expect(page.getByRole('heading', { name: 'Your space, Updated.' })).toBeVisible();
  await page.getByRole('button', { name: 'Sign out', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Good to see you.' })).toBeVisible();
  const session = await page.request.get('/api/v1/session/');
  expect(session.ok()).toBe(true);
  expect((await session.json()).user).toBeNull();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Good to see you.' })).toBeVisible();
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Your space, Updated.' })).toBeVisible();
  await expect(page.getByLabel('First name')).toHaveValue('Updated');
});
test('release calendar and detail use actual published release data', async ({ page }) => {
  await page.goto('/releases');
  await page.getByRole('link', { name: 'Coming soon', exact: true }).click();
  await expect(page.locator('.release-card').first()).toBeVisible();
  await page.locator('.release-card').first().click();
  await expect(page.getByRole('button', { name: 'Keep me in the loop' })).toBeVisible();
});
test('keyboard and automated accessibility checks on main surfaces', async ({ page }) => {
  for (const route of ['/', '/shop', '/products/velocity-02', '/cart', '/account', '/releases']) {
    await page.goto(route);
    await page.locator('h1').first().waitFor();
    const result = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
      .analyze();
    expect(
      result.violations,
      `${route}: ${JSON.stringify(result.violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })))}`,
    ).toEqual([]);
  }
  await page.goto('/');
  await page.screenshot({ path: '../docs/screenshots/home-desktop.png', fullPage: true });
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
});
for (const width of [320, 375, 390, 430, 768, 1024, 1280, 1440, 1920]) {
  test(`responsive layouts do not overflow at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const route of ['/', '/shop', '/products/velocity-02', '/cart', '/account']) {
      await page.goto(route);
      await page.locator('h1').first().waitFor();
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
        route,
      ).toBe(true);
      if (route === '/' && width === 390) {
        await page.screenshot({ path: '../docs/screenshots/home-mobile.png', fullPage: true });
      }
    }
    if ([375, 390, 430].includes(width)) {
      await page.goto('/shop');
      await page.getByRole('button', { name: 'Filters', exact: true }).click();
      await expect(page.getByRole('dialog')).toBeVisible();
      await page.getByRole('button', { name: /Show \d+ pairs/ }).click();
      await page.screenshot({ path: `../docs/screenshots/catalog-${width}.png`, fullPage: true });
    }
  });
}
