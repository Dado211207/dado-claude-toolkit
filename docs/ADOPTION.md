# Adoption

Which profile fits which project, and what adopting one actually involves.

The profiles live in [`profiles/`](../profiles/) and each has its own README with the
detail. This page is the decision.

## Pick a profile

| Your project | Profile | Plugins |
| --- | --- | --- |
| Anything; you want the smallest useful footprint | [`01-minimal-general`](../profiles/01-minimal-general/) | `dado-core` |
| A website or web app (React, Vite, TypeScript, static HTML, Netlify) | [`02-react-vite-netlify`](../profiles/02-react-vite-netlify/) | + `dado-web-quality`, `dado-ui-design` |
| A Python desktop app packaged for Windows | [`03-python-windows-desktop`](../profiles/03-python-windows-desktop/) | + `dado-python-windows`, `dado-ui-design`, `dado-release-safety` |
| A content-heavy site in two languages | [`04-bilingual-content-site`](../profiles/04-bilingual-content-site/) | + `dado-content-localization`, `dado-web-quality`, `dado-ui-design` |
| Anything with real users in production | [`05-release-sensitive`](../profiles/05-release-sensitive/) | + `dado-release-safety` |

Profile 05 layers on top of a stack profile rather than replacing it.

## What adoption involves

1. Install the plugins ([INSTALL.md](INSTALL.md)).
2. Copy the profile's `settings.json` to `.claude/settings.json` — **merge by hand**
   if one exists.
3. Append `CLAUDE.md.snippet.md` to `CLAUDE.md` and fill in the real commands.
4. Copy the config or template files the profile lists, and edit them. They ship as
   placeholders on purpose.
5. Optionally copy `docs/ai/PROJECT_STATE.template.md` to `docs/ai/PROJECT_STATE.md`.

**Nothing modifies a repository on its own.** Every step above is you copying a file.

## The step people skip

Step 4. A profile's config file is placeholders (`<Example Organisation Name>`,
`<command>`). Left unfilled, reviews argue with assumed defaults instead of your
requirements, and a content review flags everything because there is no approved
source of facts.

If you adopt only one thing from profile 04, make it
`docs/ai/CONTENT-FACTS.md`. If you adopt only one thing from profile 02, make it
`.claude/dado-web-quality.json`.

## Start small

The `CLAUDE.md` snippet is the highest-value, lowest-risk part. It is plain text, it
works in every surface including cloud sessions, and it needs no plugin installed at
all. Add that first, live with it, then install plugins if you want the namespaced
skills and the hooks.

## Removing it

[UNINSTALL.md](UNINSTALL.md). Short version: uninstall the plugins, remove the
marketplace, delete two blocks from `.claude/settings.json` and one section from
`CLAUDE.md`. Keep the deny rules and your approved-facts files — they are useful
without the toolkit.
