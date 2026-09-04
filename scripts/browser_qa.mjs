#!/usr/bin/env node

import { mkdir } from 'node:fs/promises';
import { chromium } from 'playwright';

const baseUrl = process.env.BASE_URL || 'http://127.0.0.1:8000';
const screenshotDir = 'artifacts/browser-qa';

const pages = [
  ['home', 'index.html'],
  ['activities', 'activities.html'],
  ['listings', 'listings.html'],
  ['guides', 'guides.html'],
  ['about', 'about.html'],
  ['contact', 'contact.html'],
  ['404', '404.html'],
];

const viewports = [
  ['desktop', { width: 1440, height: 900 }],
  ['mobile', { width: 390, height: 844 }],
];

const errors = [];
const record = (condition, message) => {
  if (!condition) errors.push(message);
};

const settleRevealAnimations = async (page) => {
  const revealItems = page.locator('.reveal');
  const count = await revealItems.count();

  for (let index = 0; index < count; index += 1) {
    await revealItems.nth(index).scrollIntoViewIfNeeded();
    await page.waitForTimeout(45);
  }

  await page.waitForFunction(
    () => Array.from(document.querySelectorAll('.reveal')).every((node) => node.classList.contains('is-visible')),
    undefined,
    { timeout: 5_000 },
  );

  // The CSS reveal transition is 0.6s. Wait for its final visual state
  // so screenshots represent the settled page rather than an animation frame.
  await page.waitForTimeout(700);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(80);
};

await mkdir(screenshotDir, { recursive: true });

const browser = await chromium.launch({ headless: true });

try {
  for (const [viewportName, viewport] of viewports) {
    const context = await browser.newContext({ viewport });

    try {
      for (const [pageName, path] of pages) {
        const page = await context.newPage();
        const prefix = `${viewportName}/${pageName}`;
        const runtimeErrors = [];

        page.on('pageerror', (error) => runtimeErrors.push(`pageerror: ${error.message}`));
        page.on('console', (message) => {
          if (message.type() === 'error') runtimeErrors.push(`console: ${message.text()}`);
        });

        try {
          const response = await page.goto(`${baseUrl}/${path}`, {
            waitUntil: 'load',
            timeout: 15_000,
          });

          record(Boolean(response?.ok()), `${prefix}: HTTP response was not successful`);
          await page.waitForTimeout(120);

          const h1 = page.locator('h1').first();
          record((await h1.count()) === 1, `${prefix}: expected one primary H1`);
          if ((await h1.count()) === 1) {
            record(await h1.isVisible(), `${prefix}: primary H1 is not visible`);
          }

          const overflow = await page.evaluate(() => ({
            clientWidth: document.documentElement.clientWidth,
            scrollWidth: Math.max(
              document.documentElement.scrollWidth,
              document.body?.scrollWidth || 0,
            ),
          }));
          record(
            overflow.scrollWidth <= overflow.clientWidth + 1,
            `${prefix}: horizontal overflow ${overflow.scrollWidth}px > ${overflow.clientWidth}px`,
          );

          const nav = page.locator('[data-site-nav]');
          const menuButton = page.locator('[data-menu-button]');
          record((await nav.count()) === 1, `${prefix}: site navigation not found`);
          record((await menuButton.count()) === 1, `${prefix}: menu button not found`);

          if ((await nav.count()) === 1 && (await menuButton.count()) === 1) {
            if (viewportName === 'desktop') {
              record(await nav.isVisible(), `${prefix}: desktop navigation is not visible`);
              record(!(await nav.evaluate((node) => node.hasAttribute('inert'))), `${prefix}: desktop navigation is inert`);
              record(!(await menuButton.isVisible()), `${prefix}: mobile menu button is visible on desktop`);
            } else {
              record(await menuButton.isVisible(), `${prefix}: mobile menu button is not visible`);
              record((await menuButton.getAttribute('aria-expanded')) === 'false', `${prefix}: mobile menu does not start closed`);
              record(await nav.evaluate((node) => node.hasAttribute('inert')), `${prefix}: closed mobile navigation is not inert`);

              await menuButton.focus();
              await menuButton.click();
              record((await menuButton.getAttribute('aria-expanded')) === 'true', `${prefix}: mobile menu did not open`);
              record(!(await nav.evaluate((node) => node.hasAttribute('inert'))), `${prefix}: open mobile navigation is still inert`);

              await menuButton.focus();
              await page.keyboard.press('Tab');
              record(
                await page.evaluate(() => Boolean(document.activeElement?.closest('[data-site-nav]'))),
                `${prefix}: Tab from menu trigger did not enter open navigation`,
              );

              await page.keyboard.press('Escape');
              record((await menuButton.getAttribute('aria-expanded')) === 'false', `${prefix}: Escape did not close mobile menu`);
              record(await nav.evaluate((node) => node.hasAttribute('inert')), `${prefix}: mobile navigation is not inert after Escape`);
              record(await menuButton.evaluate((node) => document.activeElement === node), `${prefix}: focus did not return to menu trigger after Escape`);
            }
          }

          await settleRevealAnimations(page);
        } catch (error) {
          errors.push(`${prefix}: ${error instanceof Error ? error.message : String(error)}`);
        } finally {
          try {
            await page.screenshot({
              path: `${screenshotDir}/${viewportName}-${pageName}.png`,
              fullPage: true,
            });
          } catch (error) {
            errors.push(`${prefix}: screenshot failed: ${error instanceof Error ? error.message : String(error)}`);
          }

          runtimeErrors.forEach((message) => errors.push(`${prefix}: ${message}`));
          await page.close();
        }
      }
    } finally {
      await context.close();
    }
  }
} finally {
  await browser.close();
}

if (errors.length) {
  console.error(`Browser QA failed with ${errors.length} issue(s):`);
  errors.forEach((error) => console.error(`- ${error}`));
  process.exit(1);
}

console.log(`Browser QA passed for ${pages.length} pages across ${viewports.length} viewports.`);
console.log(`Saved ${pages.length * viewports.length} settled screenshots to ${screenshotDir}.`);
