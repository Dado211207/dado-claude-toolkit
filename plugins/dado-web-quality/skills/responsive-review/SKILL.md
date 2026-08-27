---
name: responsive-review
description: Check layout across a viewport matrix for horizontal overflow, clipped or truncated text, broken headers, undersized touch targets and failed images. Use when reviewing a site's layout, after a CSS or component change, or when something looks wrong on mobile.
---

# Responsive layout review

Measure. Reading CSS tells you what was intended; only a rendered page tells you
what happens.

## Viewport matrix

Use the project's matrix from `.claude/dado-web-quality.json` if present. Otherwise
say you are assuming these, and use them:

| Name | Width × Height | Why |
| --- | --- | --- |
| mobile-small | 320 × 568 | The narrowest width still worth supporting |
| mobile | 390 × 844 | Common modern phone |
| tablet | 768 × 1024 | Where layouts usually switch |
| laptop | 1280 × 800 | Most common desktop viewport |
| desktop | 1920 × 1080 | Wide layouts, max-width behaviour |

Also check one long-content page at a short viewport height, and one page at 200%
browser zoom — zoom breaks layouts that width alone does not.

## 1. Horizontal overflow

The page body must never scroll sideways. Measure it, do not eyeball it:

```js
// in the page context
const de = document.documentElement;
de.scrollWidth - de.clientWidth            // > 0 means the page overflows
```

To find the culprit, look for elements wider than the viewport:

```js
[...document.querySelectorAll('*')]
  .filter(el => el.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
  .slice(0, 20)
  .map(el => ({ tag: el.tagName, cls: el.className, right: Math.round(el.getBoundingClientRect().right) }))
```

Usual causes: a fixed pixel width, `100vw` next to a scrollbar, an unwrapped long
string or URL, a wide table, a negative margin, an absolutely positioned decoration,
a grid whose `minmax()` floor exceeds the viewport.

Note: wide content *inside* its own `overflow-x: auto` container is correct. The
defect is the page body scrolling.

## 2. Clipped and truncated text

Distinguish deliberate truncation (an ellipsis with the full text available
elsewhere) from accidental clipping (text cut by `overflow: hidden`, a fixed height,
or `white-space: nowrap`).

```js
[...document.querySelectorAll('*')]
  .filter(el => el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1)
```

Check especially: headings at 320px, buttons whose label is longer in the second
language, nav items, badge and chip text, form labels and validation messages.

## 3. Header and navigation

At every viewport:

- the header does not overlap the content beneath it
- a sticky or fixed header leaves the right amount of space (see anchor offsets in
  `/dado-web-quality:routing-and-navigation`)
- the mobile menu opens, is reachable, closes, and traps nothing when closed
- the logo and the nav do not collide at the narrowest width
- the header does not change height in a way that shifts content after load

## 4. Touch targets

Interactive elements need at least the project's minimum (default 44×44 CSS px)
including padding, and must not overlap each other.

```js
[...document.querySelectorAll('a, button, input, select, textarea, [role="button"]')]
  .map(el => ({ el, r: el.getBoundingClientRect() }))
  .filter(({ r }) => r.width > 0 && (r.width < 44 || r.height < 44))
```

## 5. Images and media

- every `<img>` has an intrinsic size or an aspect ratio, so it does not cause layout
  shift on load
- `naturalWidth === 0` after load means the image failed — list the failing URLs
- responsive images resolve a sensible candidate at each viewport
- videos and iframes scale down rather than forcing a minimum width

## 6. Report

One line per finding, most severe first:

```
[overflow|clip|header|touch-target|image]  <route>  <viewport>  <browser>
  Observed: <the measurement, with numbers>
  Element:  <selector>
  Cause:    <the actual CSS or content reason>
  Fix:      <the smallest change>
```

Report the measurement, not an impression. "Overflows by 18px at 320px wide because
`.hero` has `min-width: 340px`" is actionable; "looks cramped on mobile" is not.

State which viewports and browsers you actually rendered, and which you did not.
