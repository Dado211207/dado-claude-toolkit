---
name: routing-and-navigation
description: Verify routes and 404 handling, scroll-to-top on navigation, browser back/forward scroll restoration, anchor offsets under a sticky header, and reveal-animation behaviour. Use after changing routing, navigation, scroll handling or on-scroll animations, or when back-button behaviour is reported as wrong.
---

# Routing, scroll and navigation behaviour

These defects are invisible in a screenshot and obvious to a user. Each one below is
checked by performing the interaction, not by reading the router config.

## 1. Routes resolve

For every route the project defines:

- it renders without a client-side error
- it returns the right HTTP status on a **hard load** (not just a client-side push)
- deep links work: open the URL directly, not by navigating from the home page

For an SPA, a hard load of a nested route only works if the host rewrites unknown
paths to `index.html`. Check the host config
(`_redirects`, `netlify.toml`, `vercel.json`) — see
`/dado-web-quality:headers-and-hosting`.

## 2. The 404 route

A missing path must produce the site's 404 page **and** a 404 status:

```
curl -s -o /dev/null -w "%{http_code}\n" <origin>/definitely-not-a-real-route
```

The common SPA failure: the rewrite sends every unknown path to `index.html` with
status 200, so the 404 page renders but search engines and monitoring see success.
Report the status and the rendered page separately.

Check too that the 404 page has working navigation back into the site, and its own
`<title>` and `<h1>`.

## 3. Scroll-to-top on navigation

Navigating to a new route should start at the top. Test it from a scrolled position:

1. scroll to the bottom of a long route
2. click a link to another route
3. the new route starts at scroll position 0

A router that preserves scroll across route changes lands users mid-page on arrival.

Do not scroll-to-top on a same-page anchor, on a query-string-only change, or on a
back/forward navigation — those have their own rules below.

## 4. Back/forward scroll restoration

Browsers restore scroll on history navigation by default
(`history.scrollRestoration === 'auto'`). Custom scroll handling frequently breaks it.

1. scroll to the middle of route A
2. navigate to route B
3. press Back

Route A must return to the position you left. If the app sets
`scrollRestoration = 'manual'`, it must then restore the position itself — verify it
does, per route, including for routes whose content loads asynchronously.

Check Forward as well; it is usually forgotten.

## 5. Anchor offsets under a sticky header

With a sticky or fixed header, a `#section` link must not place the target under it.

- open `<origin>/<route>#<section>` directly, as a hard load
- click an in-page anchor from a scrolled position
- use the browser's find-and-jump

The fix is `scroll-margin-top` on the targets (which the browser honours for all
three cases), not a JavaScript offset applied on click. Verify the offset matches the
header's actual height at each viewport — headers are often taller on mobile.

Also confirm the anchor target receives focus, not just scroll, so keyboard users
land in the right place.

## 6. Reveal animations

On-scroll reveals fail in specific, checkable ways:

- **Content above the fold** must be visible immediately, not waiting for a scroll
  event that never fires.
- **Content already in view on load** must reveal. `IntersectionObserver` fires on
  observe, but only if the observer is attached after layout.
- **Fast scrolling** past an element must not leave it invisible.
- **Back navigation** to a page must not show a blank page of un-revealed content.
- **Printing** and **`prefers-reduced-motion`** must show all content — an element
  stuck at `opacity: 0` is content loss, not a missing animation.

Test each by loading the route at a scrolled position, and by reloading mid-page.

## 7. Report

```
[route|404|scroll-top|restoration|anchor|reveal]  <route>  <viewport>  <browser>
  Steps:    <the exact interaction>
  Expected: <what should happen>
  Observed: <what happened>
  Cause:    <the code or config responsible>
```

Say which browsers you performed these in. Scroll restoration differs between
Chromium, Firefox and WebKit; a result from one is not a result for all three.
