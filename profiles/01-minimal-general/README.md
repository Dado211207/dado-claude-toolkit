# Profile 01 — minimal / general repository

The smallest useful adoption. Suitable for any repository, any language.

## Plugins

| Plugin | Why |
| --- | --- |
| `dado-core` | Orientation, planning, evidence-first debugging, safe editing, test selection, honest verification |

Nothing else. Add a stack profile on top when the project needs one.

## Install

```bash
claude plugin marketplace add Dado211207/dado-claude-toolkit
claude plugin install dado-core@dado-tools
```

Or, inside a Claude Code session:

```
/plugin marketplace add Dado211207/dado-claude-toolkit
/plugin install dado-core@dado-tools
```

Confirm the trust prompt yourself. See [`docs/INSTALL.md`](../../docs/INSTALL.md) for
scopes, pinning to a ref, and what to do in a cloud session where `/plugin` is not
available.

## Files to copy

| From | To | Note |
| --- | --- | --- |
| `settings.json` | `.claude/settings.json` | Merge by hand if the project has one |
| `CLAUDE.md.snippet.md` | append to `CLAUDE.md` | |
| `docs/ai/PROJECT_STATE.template.md` (repo root of this toolkit) | `docs/ai/PROJECT_STATE.md` | Optional |

## Required tools

| Tool | Needed for | If missing |
| --- | --- | --- |
| `git` | Everything | Nothing works; this is a git-centred workflow |
| `python3` | The `dado-core` secret-file hook | The hook is inert. Skills still work |

No other dependencies. `dado-core` adds no runtime dependency to your project.

## Suggested verification commands

There is no universal command set — use the project's own. Record them in
`CLAUDE.md` so Claude does not have to guess:

```
Build:     <the project's build command>
Test:      <the project's test command>
Lint:      <the project's lint command>
Typecheck: <the project's typecheck command>
```

If the project defines none, say so in `CLAUDE.md` rather than leaving it blank —
"no automated tests" is useful information.

## What remains manual

- Installing the plugin, and confirming the trust prompt.
- Deciding what goes in `PROJECT_STATE.md`, and keeping it current.
- Every merge, tag, release and deployment.
- Judging whether a report's claims are true. The plugin makes claims checkable; it
  does not make them true.

## Remove it cleanly

```bash
claude plugin uninstall dado-core@dado-tools
claude plugin marketplace remove dado-tools     # optional
```

Then, in your repository:

1. Remove the `extraKnownMarketplaces` and `enabledPlugins` blocks from
   `.claude/settings.json`. Keep the `permissions.deny` rules if you want them —
   they are independent of the toolkit.
2. Remove the snippet from `CLAUDE.md`.
3. `docs/ai/PROJECT_STATE.md` is your file. Delete it or keep it.

Nothing else is left behind. The plugin writes no files into your repository.
