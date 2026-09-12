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
  ['learning', 'learning.html'],
  ['volunteering', 'volunteering.html'],
  ['sports', 'sports.html'],
  ['culture-library', 'culture-library.html'],
  ['about', 'about.html'],
  ['contact', 'contact.html'],
  ['site-info', 'site-info.html'],
  ['privacy-policy', 'privacy-policy.html'],
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

// Mirrors assets/listings-filter.js so period/expiry expectations stay data-driven
// instead of hardcoding today's card counts.
const parseISODate = (value) => {
  if (!value) return null;
  const [year, month, day] = value.split('-').map(Number);
  if (!year || !month || !day) return null;
  return new Date(year, month - 1, day);
};

const startOfDay = (value) => {
  const copy = new Date(value);
  copy.setHours(0, 0, 0, 0);
  return copy;
};

const endOfWeek = (base) => {
  const copy = new Date(base);
  const daysUntilSunday = (7 - copy.getDay()) % 7;
  copy.setDate(copy.getDate() + daysUntilSunday);
  return copy;
};

const endOfMonth = (base) => new Date(base.getFullYear(), base.getMonth() + 1, 0);

const getPeriodEnd = (period, base) => {
  if (period === 'week') return endOfWeek(base);
  if (period === 'month') return endOfMonth(base);
  return null;
};

const cardIsExpired = (data, today) => {
  if (data.kind !== 'event') return false;

  if (data.occurrenceDates) {
    const dates = data.occurrenceDates.split(',').map((value) => parseISODate(value.trim())).filter(Boolean);
    if (dates.length === 0) return false;
    return dates.every((date) => date < today);
  }

  const endDate = parseISODate(data.endDate) || parseISODate(data.startDate);
  if (!endDate) return false;
  return endDate < today;
};

const cardMatchesPeriod = (data, period, today) => {
  if (period === 'all') return true;

  const end = getPeriodEnd(period, today);

  if (data.occurrenceDates) {
    const dates = data.occurrenceDates.split(',').map((value) => parseISODate(value.trim())).filter(Boolean);
    return dates.some((date) => date >= today && date <= end);
  }

  const startDate = parseISODate(data.startDate);
  const endDate = parseISODate(data.endDate);
  if (!startDate && !endDate) return false;

  const effectiveStart = startDate || endDate;
  const effectiveEnd = endDate || startDate;
  return effectiveStart <= end && effectiveEnd >= today;
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

const checkListingsFilters = async (page, prefix) => {
  const search = page.locator('[data-listing-search]');
  const count = page.locator('[data-listing-count]');
  const empty = page.locator('[data-listing-empty]');
  const allButton = page.locator('[data-listing-kind="all"]');
  const eventButton = page.locator('[data-listing-kind="event"]');
  const resourceButton = page.locator('[data-listing-kind="resource"]');
  const periodAllButton = page.locator('[data-listing-period="all"]');
  const periodWeekButton = page.locator('[data-listing-period="week"]');
  const periodMonthButton = page.locator('[data-listing-period="month"]');
  const cards = page.locator('[data-listing-card]');
  const eventCards = page.locator('[data-listing-card][data-kind="event"]');
  const resourceCards = page.locator('[data-listing-card][data-kind="resource"]');
  const resourceSection = page.locator('[data-listing-section="resource"]');
  const eventSection = page.locator('[data-listing-section="event"]');
  const visibleCards = () => page.locator('[data-listing-card]:visible').count();

  record((await search.count()) === 1, `${prefix}: listing search input not found`);
  record((await count.count()) === 1, `${prefix}: listing result count not found`);
  record((await allButton.count()) === 1, `${prefix}: all listings filter not found`);
  record((await eventButton.count()) === 1, `${prefix}: event listings filter not found`);
  record((await periodAllButton.count()) === 1, `${prefix}: period all filter not found`);
  record((await periodWeekButton.count()) === 1, `${prefix}: period week filter not found`);
  record((await periodMonthButton.count()) === 1, `${prefix}: period month filter not found`);

  if ((await search.count()) !== 1 || (await allButton.count()) !== 1 || (await eventButton.count()) !== 1) return;

  const periodControlsPresent = (await periodAllButton.count()) === 1
    && (await periodWeekButton.count()) === 1
    && (await periodMonthButton.count()) === 1;

  if (periodControlsPresent) {
    record((await periodAllButton.getAttribute('aria-pressed')) === 'true', `${prefix}: period all filter should start pressed`);
    record((await periodWeekButton.getAttribute('aria-pressed')) === 'false', `${prefix}: period week filter should start unpressed`);
    record((await periodMonthButton.getAttribute('aria-pressed')) === 'false', `${prefix}: period month filter should start unpressed`);
  }

  const totalCards = await cards.count();
  const totalEvents = await eventCards.count();
  const totalResources = await resourceCards.count();
  record(totalCards > 0, `${prefix}: expected at least one verified listing`);
  record((await visibleCards()) === totalCards, `${prefix}: not all listings are visible before filtering`);
  record((await count.textContent())?.trim() === `${totalCards}件を表示中`, `${prefix}: initial result count is incorrect`);

  if (totalCards > 0) {
    const firstTitle = (await cards.first().locator('h3').textContent())?.trim() || '';
    const cardTexts = await cards.allTextContents();
    const expectedMatches = cardTexts.filter((text) => text.includes(firstTitle)).length;

    await search.fill(firstTitle);
    await page.waitForTimeout(60);
    record((await visibleCards()) === expectedMatches, `${prefix}: keyword search result count is incorrect`);
    record((await count.textContent())?.trim() === `${expectedMatches}件を表示中`, `${prefix}: keyword result label is incorrect`);
  }

  await search.fill('');
  if (totalEvents > 0) {
    await eventButton.click();
    await page.waitForTimeout(60);
    record((await eventButton.getAttribute('aria-pressed')) === 'true', `${prefix}: event filter aria state is incorrect`);
    record((await visibleCards()) === totalEvents, `${prefix}: event filter result count is incorrect`);
    record((await count.textContent())?.trim() === `${totalEvents}件を表示中`, `${prefix}: event result label is incorrect`);
    record(await eventSection.isVisible(), `${prefix}: event section should remain visible for event-only filtering`);
    if (totalResources > 0) record(await resourceSection.isHidden(), `${prefix}: resource section should hide for event-only filtering`);
  }

  await allButton.click();

  if (periodControlsPresent) {
    const cardData = await cards.evaluateAll((nodes) => nodes.map((node) => ({
      kind: node.dataset.kind,
      startDate: node.dataset.startDate,
      endDate: node.dataset.endDate,
      occurrenceDates: node.dataset.occurrenceDates,
    })));
    const today = startOfDay(new Date());
    const nonExpiredData = cardData.filter((data) => !cardIsExpired(data, today));

    const expectedForPeriod = (period) => nonExpiredData.filter(
      (data) => data.kind === 'event' && cardMatchesPeriod(data, period, today),
    ).length;

    const expectedWeek = expectedForPeriod('week');
    await periodWeekButton.click();
    await page.waitForTimeout(60);
    record((await periodWeekButton.getAttribute('aria-pressed')) === 'true', `${prefix}: period week aria state is incorrect`);
    record((await periodAllButton.getAttribute('aria-pressed')) === 'false', `${prefix}: period all aria state did not clear for week filter`);
    record((await eventButton.getAttribute('aria-pressed')) === 'true', `${prefix}: week period filter should switch kind filter to event`);
    record((await visibleCards()) === expectedWeek, `${prefix}: week period result count is incorrect`);
    record((await count.textContent())?.trim() === `${expectedWeek}件を表示中`, `${prefix}: week period result label is incorrect`);
    if (totalResources > 0) record(await resourceSection.isHidden(), `${prefix}: resource section should hide while period filter forces event kind`);
    record((await eventSection.isVisible()) === (expectedWeek > 0), `${prefix}: event section visibility is incorrect for week period`);

    const expectedMonth = expectedForPeriod('month');
    await periodMonthButton.click();
    await page.waitForTimeout(60);
    record((await periodMonthButton.getAttribute('aria-pressed')) === 'true', `${prefix}: period month aria state is incorrect`);
    record((await periodWeekButton.getAttribute('aria-pressed')) === 'false', `${prefix}: period week aria state did not clear for month filter`);
    record((await eventButton.getAttribute('aria-pressed')) === 'true', `${prefix}: month period filter should keep kind filter on event`);
    record((await visibleCards()) === expectedMonth, `${prefix}: month period result count is incorrect`);
    record((await count.textContent())?.trim() === `${expectedMonth}件を表示中`, `${prefix}: month period result label is incorrect`);
    record((await eventSection.isVisible()) === (expectedMonth > 0), `${prefix}: event section visibility is incorrect for month period`);

    if ((await resourceButton.count()) === 1) {
      const expectedResources = nonExpiredData.filter((data) => data.kind === 'resource').length;
      await resourceButton.click();
      await page.waitForTimeout(60);
      record((await resourceButton.getAttribute('aria-pressed')) === 'true', `${prefix}: resource filter aria state is incorrect`);
      record((await periodAllButton.getAttribute('aria-pressed')) === 'true', `${prefix}: switching to resource kind should reset period filter to all`);
      record((await visibleCards()) === expectedResources, `${prefix}: resource filter result count is incorrect`);
      if (totalEvents > 0) record(await eventSection.isHidden(), `${prefix}: event section should hide for resource-only filtering`);
      if (expectedResources > 0) record(await resourceSection.isVisible(), `${prefix}: resource section should remain visible for resource-only filtering`);
    }

    await allButton.click();
    await periodAllButton.click();
    await page.waitForTimeout(60);
  }

  await search.fill('50PLUS-NO-MATCH-QUERY');
  await page.waitForTimeout(60);
  record((await visibleCards()) === 0, `${prefix}: no-match search should show zero cards`);
  record(await empty.isVisible(), `${prefix}: no-match message is not visible`);
  record((await count.textContent())?.trim() === '0件を表示中', `${prefix}: no-match result count is incorrect`);

  await search.fill('');
  await allButton.click();
  await page.waitForTimeout(60);
  record((await visibleCards()) === totalCards, `${prefix}: reset did not restore all listings`);
  if (totalResources > 0) record(await resourceSection.isVisible(), `${prefix}: resource section did not return after reset`);
  if (totalEvents > 0) record(await eventSection.isVisible(), `${prefix}: event section did not return after reset`);
};

// Far enough past every event date in the current dataset that runtime expiry
// is exercised deterministically without editing repository data.
const FAR_FUTURE_CLOCK = '2999-01-01T00:00:00';

const expiryPages = [
  ['listings', 'listings.html'],
  ['learning', 'learning.html'],
  ['volunteering', 'volunteering.html'],
  ['sports', 'sports.html'],
  ['culture-library', 'culture-library.html'],
];

const checkEventExpiryUnderFutureClock = async (browser, pageName, path) => {
  const prefix = `expiry/${pageName}`;
  const context = await browser.newContext({ viewport: viewports[0][1] });

  try {
    const page = await context.newPage();
    const runtimeErrors = [];
    page.on('pageerror', (error) => runtimeErrors.push(`pageerror: ${error.message}`));
    page.on('console', (message) => {
      if (message.type() === 'error') runtimeErrors.push(`console: ${message.text()}`);
    });

    try {
      await page.clock.setFixedTime(new Date(FAR_FUTURE_CLOCK));

      const response = await page.goto(`${baseUrl}/${path}`, { waitUntil: 'load', timeout: 15_000 });
      record(Boolean(response?.ok()), `${prefix}: HTTP response was not successful`);
      await page.waitForTimeout(120);

      const eventCards = page.locator('[data-listing-card][data-kind="event"]');
      const resourceCards = page.locator('[data-listing-card][data-kind="resource"]');
      const totalEvents = await eventCards.count();
      const totalResources = await resourceCards.count();

      record(totalEvents > 0, `${prefix}: expected at least one event card to test expiry against`);
      if (totalEvents > 0) {
        const visibleEvents = await page.locator('[data-listing-card][data-kind="event"]:visible').count();
        record(visibleEvents === 0, `${prefix}: event cards are still visible under a far-future clock`);
      }

      if (totalResources > 0) {
        const visibleResources = await page.locator('[data-listing-card][data-kind="resource"]:visible').count();
        record(visibleResources === totalResources, `${prefix}: resource cards should remain visible under a far-future clock`);
      }

      runtimeErrors.forEach((message) => errors.push(`${prefix}: ${message}`));
    } finally {
      await page.close();
    }
  } catch (error) {
    errors.push(`${prefix}: ${error instanceof Error ? error.message : String(error)}`);
  } finally {
    await context.close();
  }
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
          if (pageName === 'listings') await checkListingsFilters(page, prefix);
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

  for (const [pageName, path] of expiryPages) {
    await checkEventExpiryUnderFutureClock(browser, pageName, path);
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
