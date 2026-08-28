# Profile 02 — React / Vite / TypeScript site on Netlify

For a website or web application built with Vite (React or otherwise), typically in
TypeScript, deployed to Netlify. Adapt freely: `dado-web-quality` reads the manifests
that actually exist rather than assuming this stack.

## Plugins

| Plugin | Why |
| --- | --- |
| `dado-core` | Orientation, safe editing, test selection, honest reporting |
| `dado-web-quality` | Responsive layout, accessibility, routing, metadata, headers, browser testing, deploy previews |
| `dado-ui-design` | Coherent visual direction, design systems, interaction, typography, color and stack-specific UI guidance |

Add `dado-release-safety` (profile 05) once the site has real users.
Add `dado-content-localization` (profile 04) if the site is bilingual.

## Install

```bash
claude plugin marketplace add Dado211207/dado-claude-toolkit
claude plugin install dado-core@dado-tools
claude plugin install dado-web-quality@dado-tools
claude plugin install dado-ui-design@dado-tools
```

## Files to copy

| From | To | Note |
| --- | --- | --- |
| `settings.json` | `.claude/settings.json` | Merge by hand if one exists |
| `CLAUDE.md.snippet.md` | append to `CLAUDE.md` | Fill in the real commands and routes |
| `plugins/dado-web-quality/config/web-quality.config.example.json` | `.claude/dado-web-quality.json` | **Edit every value** — the shipped file is placeholders |

The config file is where your project's real thresholds live: viewport matrix,
browsers, minimum touch target, supported languages, routes and expected statuses,
required security headers, protected strings, forbidden copy. Without it, a review
argues with assumed defaults instead of your requirements.

## Required tools

| Tool | Needed for | If missing |
| --- | --- | --- |
| Node + the project's package manager | Build, dev server, tests | Nothing runs |
| `@playwright/test` + browser binaries | Rendered layout, routing, screenshots | Those checks become `not-run`; only static review is possible |
| `@axe-core/playwright` or `axe-core` | The automated accessibility pass | Manual a11y checks still apply; automated pass is `not-run` |
| Lighthouse / `@lhci/cli` | Performance and SEO scores | Reported as `not-run` |
| `curl` | Header and redirect checks against a live URL | Config review only, labelled as intent not behaviour |
| Network egress to the preview/production URL | Deploy preview verification | Reported as `not-run` |

**The plugin never installs any of these into your project.** Missing tooling becomes
a `not-run` line naming what it leaves unverified.

Chromium, Firefox and WebKit are three separate Playwright downloads. Having one does
not give you cross-browser results.

## Suggested verification commands

Replace with the project's real ones:

```bash
npm run build                       # must succeed before any deploy claim
npm run typecheck                   # or: npx tsc --noEmit
npm run lint
npm run test
npx playwright test                 # only the browsers actually installed
npx playwright test --project=chromium --project=firefox --project=webkit
curl -sSI https://<preview-url>/    # headers as actually served
curl -s -o /dev/null -w "%{http_code}\n" https://<preview-url>/not-a-real-route
```

Typical design flow: `/dado-ui-design:ui-ux-pro-max` for a deliberate visual system,
then `/dado-web-quality:web-audit` to establish what can honestly be verified and run
the specific quality checks it points at.

## What remains manual

- Installing the plugins and confirming the trust prompt.
- Filling in `.claude/dado-web-quality.json` with real thresholds.
- Installing Playwright browsers, axe or Lighthouse if you want those checks.
- **Every deploy.** The deny rules make `netlify deploy` and `vercel` a decision you
  make, not a step Claude takes.
- Visual design judgement, real-font rendering, performance on real hardware, and
  screen-reader behaviour. These are `requires-manual-acceptance` and no browser
  check substitutes for them.

## Remove it cleanly

```bash
claude plugin uninstall dado-web-quality@dado-tools
claude plugin uninstall dado-ui-design@dado-tools
claude plugin uninstall dado-core@dado-tools
claude plugin marketplace remove dado-tools     # optional
```

Then remove the `extraKnownMarketplaces` and `enabledPlugins` blocks from
`.claude/settings.json`, remove the snippet from `CLAUDE.md`, and delete
`.claude/dado-web-quality.json` if you no longer want it. Keep the
`permissions.deny` rules if they are useful — they are independent of the toolkit.
