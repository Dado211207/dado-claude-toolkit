# Adoption profiles

Five starting points for adopting `dado-tools` in a project. Each profile is a
**worked example you copy from**, not something that installs itself. Nothing here
modifies any repository on its own.

| Profile | For | Plugins |
| --- | --- | --- |
| [`01-minimal-general`](01-minimal-general/) | Any repository, smallest useful footprint | `dado-core` |
| [`02-react-vite-netlify`](02-react-vite-netlify/) | React / Vite / TypeScript site on Netlify | `dado-core`, `dado-web-quality` |
| [`03-python-windows-desktop`](03-python-windows-desktop/) | Python desktop app packaged for Windows | `dado-core`, `dado-python-windows`, `dado-release-safety` |
| [`04-bilingual-content-site`](04-bilingual-content-site/) | Content-heavy site in two languages | `dado-core`, `dado-content-localization`, `dado-web-quality` |
| [`05-release-sensitive`](05-release-sensitive/) | Anything deployed to production users | `dado-core`, `dado-release-safety` (+ the stack profile) |

Each profile directory contains:

```
README.md              what it is for, required tools, verification commands,
                       what stays manual, and how to remove it cleanly
settings.json          an example .claude/settings.json to copy and edit
CLAUDE.md.snippet.md   text to append to the project's CLAUDE.md
```

## How to use one

1. Read the profile's `README.md` first, including its "what remains manual" section.
2. Copy `settings.json` into your project as `.claude/settings.json`. If the project
   already has one, **merge by hand** — do not overwrite it.
3. Append the contents of `CLAUDE.md.snippet.md` to the project's `CLAUDE.md`.
4. Install the plugins the profile lists, using the commands in
   [`docs/INSTALL.md`](../docs/INSTALL.md).
5. Confirm the trust prompt yourself when Claude Code shows it.

## Two things every profile shares

**Committing `extraKnownMarketplaces` does not install anything.** It registers where
the marketplace lives. Each person still installs the plugins themselves, and a
plugin from an external source that only project settings enable does not load until
they do. The install commands are in [`docs/INSTALL.md`](../docs/INSTALL.md).

**The permission rules are deny-only.** No profile adds an `allow` rule, because an
`allow` rule grants Claude Code the right to act without asking you. Deny rules only
restrict, they apply immediately, and they do not wait for workspace trust. Every
profile's `permissions.deny` blocks reading credential files and running the commands
that merge, publish or deploy — so those need a decision from you, in the moment.

Adjust the deny list to your project. A rule that blocks something you legitimately
do every day will get deleted wholesale, which is worse than a shorter list you keep.
