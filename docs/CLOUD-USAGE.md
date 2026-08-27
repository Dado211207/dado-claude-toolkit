# Using the toolkit in Claude Code on the web

Cloud sessions are the environment where the most claims about "always-on" tooling
turn out to be false. This page says exactly what works, what does not, and what to
do instead.

## The one difference that drives everything else

**`/plugin` is a terminal-only command and is not available in a cloud session.** The
official documentation says so directly, and points at two alternatives: the plugin
browser in the Claude desktop app, or declaring the plugin under `enabledPlugins` in
`.claude/settings.json`.

Everything below follows from that.

## What definitely works in a cloud session

| Thing | Why it works |
| --- | --- |
| `.claude/agents/*.md` in your repository | The cloud documentation states these are picked up automatically |
| `.claude/skills/<name>/SKILL.md` in your repository | Repository skills load like any other repository content |
| `CLAUDE.md` | Read as repository instructions |
| `permissions.deny` in `.claude/settings.json` | Deny rules restrict, so they apply immediately without a trust step |
| `docs/ai/PROJECT_STATE.md` | An ordinary tracked file that gets read again |
| Subagents from `.claude/agents/` | Explicitly documented for cloud sessions |

Everything on this list is **committed repository content**. That is the reliable
mechanism in the cloud, and it is why this toolkit is built around portable,
reviewable, committed configuration.

## What is documented but unverified here

Declaring the marketplace and plugins in the repository's settings:

```json
{
  "extraKnownMarketplaces": {
    "dado-tools": {
      "source": { "source": "github", "repo": "Dado211207/dado-claude-toolkit" }
    }
  },
  "enabledPlugins": {
    "dado-core@dado-tools": true
  }
}
```

Two official requirements apply:

1. Declaring a plugin under `enabledPlugins` in `.claude/settings.json` is the
   documented path **for cloud sessions**.
2. An external plugin still needs its marketplace/install trust established for the
   account or environment that loads it. A committed enablement entry is not a
   silent permission grant.

This toolkit is an external source (a GitHub repository). The declaration is the
right configuration; it is not proof that a specific account has completed the
required trust/install step.

**This repository has not verified the end-to-end behaviour in a cloud session.** It
is listed here as documented-but-unverified rather than presented as working. If you
try it, the result is worth recording in this file.

## The fallback that always works: vendor what you need

If plugin loading in a cloud session does not do what you want, copy the pieces you
actually use into the repository. They then load as ordinary repository content, with
no marketplace, no install step and no trust prompt.

```bash
# from a clone of the toolkit, run inside your target repository
mkdir -p .claude/skills .claude/agents

cp -r <toolkit>/plugins/dado-core/skills/orient            .claude/skills/
cp -r <toolkit>/plugins/dado-core/skills/verify-and-report .claude/skills/
cp    <toolkit>/plugins/dado-core/agents/final-verifier.md .claude/agents/
```

Trade-offs, stated plainly:

- **You lose the namespace.** A vendored skill is `/orient`, not `/dado-core:orient`,
  so it can collide with another skill of the same name.
- **You lose updates.** A vendored copy does not track the toolkit. You re-copy it
  yourself, and you should record which version you copied.
- **You gain certainty.** Committed repository content loads in every surface,
  including cloud sessions, with no install step.
- **Copy only what you use.** Every skill in `.claude/skills/` costs context.

Record the source and version in a comment or in `PROJECT_STATE.md` so a later reader
knows where the file came from and when to refresh it.

## The other fallback: put the rules in CLAUDE.md

Every profile ships a `CLAUDE.md.snippet.md`. The rules in it — the honest reporting
format, the stop line, the protected areas — are just text. They work with no plugin,
no skill file and no hook, in every surface including the cloud.

This is the lowest-tech option and the most reliable one. Start here.

## Hooks in a cloud session

The hooks need Python 3 exposed as `python` on `PATH` in the session's environment. Cloud environments
generally have it, but this is not a guarantee you should build on:

- If `python` is missing, a hook command fails. Claude Code treats a failing hook as
  non-blocking for these events, so the guard is simply **inert** — no error, no
  block, no protection.
- `guard_protected_branch.py` and `remind_uncommitted.py` also need `git`, which a
  cloud session has since it clones your repository.
- A hook can only fire if the plugin providing it loaded. If plugin loading is the
  uncertain part, the hooks are uncertain too.

**Never present the hooks as protection in a cloud session.** They are a convenience
where they run. The skills and the `CLAUDE.md` rules do not depend on them.

## Network access

A cloud session's network access is set by the environment's policy, chosen when the
environment was created. That affects the toolkit's checks, not the toolkit itself:

- fetching a deploy preview or production URL for header, redirect and smoke checks
- downloading Playwright browsers
- reaching a package registry

When egress is blocked, those checks are `not-run` with the reason, and the report
must say what that leaves unverified. See
https://code.claude.com/docs/en/cloud-environments for how to configure a policy.

## What a cloud session cannot do at all

- Test a microphone, a speaker, a camera, a GPU, or an antivirus product.
- Run a Windows installer, or observe a Windows permission dialog or SmartScreen.
- Judge visual design, real-font rendering, or how a page feels.
- Substitute for a human on real hardware.

`dado-python-windows` marks these `requires-manual-acceptance` and hands them back.
That is not a limitation of the toolkit; it is the honest boundary of the environment.

## Setup scripts

A cloud environment can run a setup script when a session starts — useful for
installing Python 3, Playwright browsers or project dependencies so that fewer
checks come back `not-run`. See
https://code.claude.com/docs/en/cloud-environments#setup-scripts.

Do not put credentials in a setup script. Use the environment's variable
configuration for anything sensitive, and remember that a session with network access
can send data outward.

## Recommended cloud setup, in order

1. Append the profile's `CLAUDE.md.snippet.md` to `CLAUDE.md`. **This is the part
   that always works.**
2. Commit `.claude/settings.json` with the `permissions.deny` rules. They apply
   immediately.
3. Add the `extraKnownMarketplaces` and `enabledPlugins` blocks. If the plugins load,
   you get the namespaced skills.
4. If they do not, vendor the two or three skills you use most into
   `.claude/skills/` and the agents into `.claude/agents/`.
5. Record in `PROJECT_STATE.md` which of these you did, so the next session does not
   have to work it out.
