---
name: browser-testing
description: Run browser checks reliably - console and network error capture, cross-browser runs, deterministic screenshots, before/after comparison, and honest triage of why a test failed. Use when driving Playwright or a headless browser, capturing screenshots, or explaining a failing browser test.
---

# Browser testing

## 1. Use what the project has

Read `playwright.config.*` for the browsers, base URL, timeouts and projects the
repository already defines, and use them. Do not add Playwright, add browsers, or
change the config to make a check possible — propose it instead, and record the
check as `not-run` for now.

Confirm which browser binaries are actually installed before promising cross-browser
results. `chromium`, `firefox` and `webkit` are three separate downloads; having one
does not mean having three.

```
npx playwright --version
npx playwright test --list
```

## 2. Console and network capture

Attach listeners **before** navigating, or you miss everything that happens during
load:

```js
const consoleErrors = [];
const failedRequests = [];
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => consoleErrors.push(String(e)));
page.on('requestfailed', r => failedRequests.push(`${r.url()} — ${r.failure()?.errorText}`));
page.on('response', r => { if (r.status() >= 400) failedRequests.push(`${r.status()} ${r.url()}`); });
```

Report the actual messages and URLs. Distinguish errors the site causes from noise
it does not control (a browser extension, an analytics blocker, a third-party embed).
Do not filter out an error just because it is inconvenient — say what you filtered
and why.

## 3. Determinism before assertions

A flaky screenshot or assertion is worse than none. Before capturing or asserting:

- wait for a **condition**, never a fixed sleep: `expect(locator).toBeVisible()`,
  `page.waitForLoadState('networkidle')` where appropriate, a specific response
- disable animations and transitions for the capture
- wait for web fonts: `await document.fonts.ready`
- wait for images: check every `img.complete && img.naturalWidth > 0`
- freeze anything time- or random-dependent (dates, counters, carousels)
- use a fixed viewport, fixed device scale factor, and a fixed colour scheme

```js
await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'light' });
await page.addStyleTag({ content: `*,*::before,*::after{animation:none!important;transition:none!important}` });
await page.evaluate(() => document.fonts.ready);
```

## 4. Screenshots

Name them so they can be compared later:

```
<route>__<viewport>__<browser>__<before|after>.png
```

Full-page screenshots for layout, element screenshots for a component. Capture the
same set before and after a change, from the same commit-to-commit pair, with the
same settings. A before/after pair taken with different settings proves nothing.

When reporting a visual difference, say what changed in pixels or layout terms and
which element, not "it looks better".

## 5. Cross-browser

Run Chromium, Firefox and WebKit **only if all three are installed and configured**.
Report per browser; never generalise from one:

```
chromium  <n> passed, <n> failed
firefox   <n> passed, <n> failed
webkit    not installed — not run
```

Differences worth expecting: scroll restoration, date and number formatting, focus
behaviour on buttons, `backdrop-filter`, sticky positioning edge cases, image format
support.

## 6. Triage a failure honestly

Before touching anything, classify:

| Class | Evidence needed |
| --- | --- |
| `product-defect` | The app genuinely misbehaves — reproduce it by hand |
| `test-defect` | The selector, assertion or fixture is wrong |
| `environment` | Missing browser binary, no network, no display, blocked proxy |
| `timing` | The test raced the app; identify **what** it raced |
| `flaky` | Both pass and fail observed on the same input |
| `not-run` | It never executed |

Then: **never widen a timeout to make a test pass without measuring the cause.**
Measure how long the awaited condition actually takes:

```js
const t0 = Date.now();
await expect(locator).toBeVisible({ timeout: 30_000 });
console.log('became visible after', Date.now() - t0, 'ms');
```

If it takes 200 ms and the test failed at a 5 s timeout, the timeout was not the
problem — something else was, and raising it would have hidden a real defect. If it
genuinely takes 8 s, that duration is itself a finding: report it, then decide
whether the app is slow or the wait is on the wrong condition.

Also never fix a failure by skipping the test, deleting the assertion, adding a
blanket retry, or asserting something weaker.

## 7. Report

```
Browsers run:  <list, with versions>  |  not run: <which and why>
Routes:        <list>
Console:       <n> errors — <the messages>
Network:       <n> failed — <status and URL>
Failures:      <test> — class=<…> — cause=<…> — measured=<…>
Screenshots:   <paths, and what pair was compared>
Not verified:  <what no browser check can prove — visual design judgement, real
               fonts on a real machine, performance on real hardware>
```
