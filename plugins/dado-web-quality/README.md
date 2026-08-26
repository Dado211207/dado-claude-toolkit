# dado-web-quality

A quality gate for websites and web applications: layout, accessibility, routing,
metadata, hosting headers, and honest browser-test triage.

- **Version:** 0.1.0
- **Marketplace:** `dado-tools`
- **Install:** `/plugin install dado-web-quality@dado-tools`
- **Depends on:** nothing. Pairs well with `dado-core` (honesty rules) and
  `dado-content-localization` (EN/ME copy parity, which this plugin points at but
  does not duplicate).

## Stacks

Supports React, Vite, TypeScript, JavaScript, plain static HTML/CSS and Netlify
hosting — but assumes none of them. Every skill starts by reading the manifests that
actually exist and adapting. A plain static site gets static-site checks, not
React findings.

## Skills

| Skill | Invoke | What it covers |
| --- | --- | --- |
| Web audit | `/dado-web-quality:web-audit` | Entry point: identify the stack, load thresholds, record tool availability, pick the applicable checks |
| Responsive review | `/dado-web-quality:responsive-review` | Viewport matrix, horizontal overflow, clipped text, header collisions, touch targets, image loading |
| Accessibility review | `/dado-web-quality:a11y-review` | Keyboard, focus restoration, skip link, accessible names, one-h1, landmarks, reduced motion, contrast, axe |
| Routing and navigation | `/dado-web-quality:routing-and-navigation` | Route resolution, 404 status, scroll-to-top, back/forward restoration, anchor offsets, reveal animations |
| Metadata and SEO | `/dado-web-quality:seo-and-metadata` | Per-route title/description, canonical, hreflang reciprocity, Open Graph and Twitter, sitemap, robots, structured data |
| Headers and hosting | `/dado-web-quality:headers-and-hosting` | Security and caching headers as served, Netlify `_redirects`/`_headers`/`netlify.toml`, redirect hygiene |
| Browser testing | `/dado-web-quality:browser-testing` | Console and network capture, determinism, screenshots, cross-browser runs, failure triage |
| Deploy preview check | `/dado-web-quality:deploy-preview-check` | Bind a URL to a commit, compare served bytes to a clean build, smoke pass, preview-vs-production gaps |

## Agents

| Agent | Tools | Responsibility |
| --- | --- | --- |
| `dado-web-quality:web-quality-auditor` | Read, Grep, Glob, Bash | Read-only audit with reproduction steps |
| `dado-web-quality:accessibility-reviewer` | Read, Grep, Glob, Bash | Keyboard, focus, names, headings, motion |
| `dado-web-quality:browser-test-investigator` | Read, Grep, Glob, Bash | Why a browser test fails, and its class |

No hooks. None of these agents can spawn further agents.

## Configuration

Copy `config/web-quality.config.example.json` into your project as
`.claude/dado-web-quality.json` and edit it. Nothing reads it automatically — it is a
written agreement the skills read when you point them at it, so a review argues with
your thresholds rather than with invented ones.

It configures: viewport matrix, browsers, minimum touch target, allowed horizontal
overflow, one-h1 expectation, skip-link requirement, supported languages and which
pairs must stay in sync, routes and their expected statuses, required and forbidden
security headers, caching expectations, and Lighthouse thresholds.

It also configures three string lists that make copy regressions checkable:

- `protectedStrings.organisationNames` — official names that must appear verbatim
- `protectedStrings.jobTitles` — exact titles that must not be reworded
- `protectedStrings.factualStrings` — approved wording that must survive edits
- `forbiddenCopy.strings` — wording that must never come back (old employer names,
  superseded titles, wrong locations)

The shipped file contains placeholders like `<Example Organisation Name>`, never real
content. No project's content is hard-coded into this plugin.

## What this plugin will not claim

- It does not judge visual design. "Looks better" is not a finding.
- It does not claim real-font rendering, performance on real hardware, or how a page
  feels. Those are `requires-manual-acceptance`.
- It does not claim screen-reader behaviour unless a screen reader was actually run.
- It never installs a dependency, downloads a browser, or edits a test config to make
  a check possible. Missing tooling becomes a `not-run` line with what it leaves
  unverified.
- It never widens a timeout, skips a test, or weakens an assertion to turn a failure
  green. Every timeout change must be justified by a measurement of how long the
  awaited condition actually takes.

## Uninstall

```
/plugin uninstall dado-web-quality@dado-tools
```

If you copied the config file into your project, `.claude/dado-web-quality.json` is
yours and stays until you delete it.
