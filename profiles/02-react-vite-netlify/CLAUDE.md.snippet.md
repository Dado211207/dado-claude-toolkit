<!-- Append to the project's CLAUDE.md. Edit the placeholders. -->

## Working rules

Start any non-trivial change with `/dado-core:orient`. Start any quality review with
`/dado-web-quality:web-audit`, which establishes what can honestly be checked here
before anything is claimed.

For a new page or material visual redesign, use `/dado-ui-design:ui-ux-pro-max` to
propose a coherent design system before implementation. Treat its local search
results as recommendations; project requirements and measured accessibility remain
authoritative.

### Commands (the real ones for this project)

```
Build:      <e.g. npm run build>
Dev server: <e.g. npm run dev>       (port: <…>)
Typecheck:  <e.g. npm run typecheck>
Lint:       <e.g. npm run lint>
Unit tests: <e.g. npm run test>
E2E tests:  <e.g. npx playwright test>
```

Playwright browsers installed here: `<chromium | firefox | webkit — list only what is
actually installed>`. Do not report cross-browser results for a browser that is not
installed.

### Quality thresholds

Project thresholds live in `.claude/dado-web-quality.json`. Read it before reviewing.
If a value is not there, say which default you assumed rather than presenting it as
this project's requirement.

### Routes

```
<route>   <what it is>   <expected status on a hard load>
```

### Web rules for this project

- The page body must never scroll horizontally. Wide content scrolls inside its own
  container.
- One `<h1>` per route.
- Every interactive element has a visible focus indicator and an accessible name.
- With `prefers-reduced-motion: reduce`, all reveal-animated content is still
  **visible**. An element left at `opacity: 0` is content loss, not a missing effect.
- A hard load of an unknown path returns 404, not 200 with the 404 page rendered.
- Metadata must not contradict the visible page. A title naming a different place,
  role or organisation than the body is a copy defect.
- Netlify: `_redirects` is first-match-wins and the SPA fallback belongs last.
  Verify a rule by fetching the URL, not by reading the file.

### Verification and reporting

- A check that did not run did not pass. Report `<command> -> exit <code>
  (<n> passed, <n> failed, <n> skipped)`.
- Never widen a Playwright timeout without measuring how long the awaited condition
  actually takes. Never skip a test, delete an assertion or add a blanket retry to
  turn a failure green.
- Classify every failure: `product-defect`, `test-defect`, `environment`, `timing`,
  `flaky` (both outcomes observed), or `not-run`.
- Do not install dependencies or download browsers to make a check possible. Report
  it as `not-run` and propose it.
- Never claim visual design quality, real-font rendering, performance on real
  hardware, or screen-reader behaviour that was not actually exercised.

### Stop line

No deploy, no `netlify deploy`, no merge, no tag, no release without an explicit
instruction in the current task. A green build and a green preview are not
authorisation.
