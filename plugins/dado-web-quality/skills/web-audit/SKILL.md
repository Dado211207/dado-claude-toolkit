---
name: web-audit
description: Entry point for auditing a website or web application - work out what the project actually is, which checks apply, and which tools are available before running anything. Use when asked to review, audit or quality-check a site, or before running any of the other dado-web-quality skills.
---

# Web audit: scope first

Do not start clicking. Work out what this project is and what can honestly be
checked here, then pick the checks.

## 1. Identify the project from evidence

| Look at | Tells you |
| --- | --- |
| `package.json` scripts + lockfile | Real build/dev/test commands, package manager |
| `vite.config.*`, `next.config.*`, `astro.config.*`, none | Bundler, or a plain static site |
| `tsconfig.json` | TypeScript, and whether `strict` is on |
| `src/` layout, router imports | SPA with client routing, MPA, or static HTML |
| `netlify.toml`, `public/_redirects`, `public/_headers`, `vercel.json` | Hosting and its redirect/header rules |
| `public/`, `index.html`, `<head>` | Where metadata actually lives |
| `playwright.config.*`, `*.spec.ts` | Existing browser tests and configured browsers |
| `.github/workflows/*` | What CI already enforces |

Support the stacks that are present. Do not assume React, Vite, TypeScript,
Tailwind or Netlify because the project is a website — check.

## 2. Load the project's own thresholds

If the project has `.claude/dado-web-quality.json` (copied from
`${CLAUDE_PLUGIN_ROOT}/config/web-quality.config.example.json`), read it and use its
values: viewports, browsers, touch-target size, supported languages, protected
strings, required headers, Lighthouse thresholds.

If it does not exist, say which defaults you are assuming, in the report. Never
present an assumed threshold as the project's requirement.

## 3. Establish tool availability before promising checks

Check, then record:

```
node / package manager   present? version?
project build            <command> -> exit <code>
playwright               installed? which browsers actually downloaded?
axe (@axe-core/*)        present as a dependency?
lighthouse / lhci        available?
curl                     available for header checks?
network egress           can you reach the deploy preview / production URL?
```

Anything unavailable becomes a `not-run` line in the report with what it leaves
unverified. Never substitute a weaker check and describe it as the stronger one —
reading CSS is not the same as measuring a rendered layout.

## 4. Pick the applicable checks

| Concern | Skill |
| --- | --- |
| Layout across viewports, overflow, clipping, touch targets | `/dado-web-quality:responsive-review` |
| Keyboard, focus, skip links, names, headings, reduced motion | `/dado-web-quality:a11y-review` |
| Routes, 404, scroll behaviour, anchors, reveal animations | `/dado-web-quality:routing-and-navigation` |
| Metadata, canonical, hreflang, OG/Twitter, sitemap, robots, structured data | `/dado-web-quality:seo-and-metadata` |
| Security headers, caching, Netlify redirects and headers | `/dado-web-quality:headers-and-hosting` |
| Running the browsers, screenshots, before/after | `/dado-web-quality:browser-testing` |
| Deploy preview and production comparison | `/dado-web-quality:deploy-preview-check` |

Skip what does not apply and say you skipped it. A single-language static page does
not need hreflang findings invented for it.

## 5. Report shape

```
Project:    <stack, hosting, routing model>
Config:     <project config file used | defaults assumed — which>
Tools:      <available> / <missing — and what that blocks>
Checked:    <the checks you ran>
Not run:    <check> — <reason> — leaves <what> unverified
Findings:   <severity-ordered, each with route, viewport, and how to reproduce>
```

Every finding needs a reproduction: URL or route, viewport, browser, and the exact
observation. A finding nobody can reproduce cannot be fixed or disputed.
