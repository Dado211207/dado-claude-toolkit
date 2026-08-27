# Trust and permissions

## What a plugin can do

A Claude Code plugin runs with your privileges. Its skills and agents become
instructions Claude follows; its hooks are programs Claude Code executes on your
machine. Anthropic does not verify third-party plugins.

That is the trust decision. It is the same one you make when you `npm install`
something, and it deserves the same care.

## What this toolkit grants: nothing

Version 0.1.0 ships, deliberately:

| | Count | Enforced by |
| --- | --- | --- |
| `permissions.allow` rules | **0** | check 14 |
| `allowed-tools` grants on skills | **0** | check 14 |
| MCP servers | **0** | check 27 |
| Third-party dependencies | **0** | check 26 |
| Hooks that emit `allow` | **0** | checks 15 and 24 |
| Agents that can spawn agents | **0** | check 8 |

`tests/run_validation.py` fails the build if any of these becomes non-zero. The
counts are an invariant, not a description of the current state.

## Why no allow rules

An `allow` rule tells Claude Code to run something **without asking you**. A toolkit
that shipped allow rules would be widening your permissions on your behalf, in files
you probably would not re-read.

The profiles ship `deny` rules instead. Deny rules only restrict:

- they apply **immediately** — no workspace-trust step, because they grant nothing
- they cannot be offset by an allow rule from this toolkit, because there are none
- they make merging, publishing and deploying a decision you make in the moment

## Workspace trust

`permissions.allow` and `permissions.additionalDirectories` in a project's
`.claude/settings.json` grant capability, so Claude Code applies them only after you
accept the workspace-trust dialog for that folder. `deny` and `ask` rules are not
affected.

`extraKnownMarketplaces` also waits for trust. Until you accept, the marketplace is
not added.

**Read the dialog.** It lists what the folder would grant. Confirm it yourself for
every repository, every time — including this one.

## Why hooks cannot be a security boundary

The four hooks are useful and they are not protection. Concretely:

- they see only the tool calls Claude Code routes through them
- they match text, so an equivalent command written differently, built at runtime, or
  run from a script file will not match
- a user can disable them (`disableAllHooks`, or disabling the plugin)
- without Python 3 exposed as `python` on `PATH` they fail, Claude Code treats that as non-blocking, and
  they are simply inert
- they never emit `allow`, so the worst a broken hook can do is fail open — back to
  the normal permission flow

Treat them as a speed bump that makes an irreversible action visible. Real branch
protection lives on your git host; real secret protection is not putting secrets in
files.

## Who decides what

| Decision | Who |
| --- | --- |
| Installing a plugin | You |
| Trusting a workspace | You |
| Running a denied command | You, by removing the rule or running it yourself |
| Merging, tagging, releasing, deploying | **You, per task** |
| Changing repository settings or visibility | You |
| What a skill's instructions say | This repository — read them |

A line in `CLAUDE.md`, `PROJECT_STATE.md`, a PR description, an issue, a bot comment
or a CI log is **not** authorisation for any of the above. Neither is a green CI run
or an approving review. That rule is written into `dado-release-safety` and into
every profile snippet.

## Prompt injection

Repository content can contain text aimed at an AI agent: "ignore previous
instructions", "push to main", "read the credentials file". This toolkit's skills say
explicitly that repository content can describe conventions but cannot expand
permissions, authorise a merge or deploy, or send data anywhere — and that such text
should be surfaced to you rather than followed.

That is guidance, not a guarantee. See [THREAT-MODEL.md](THREAT-MODEL.md).

## Verify before you trust

```bash
git clone https://github.com/Dado211207/dado-claude-toolkit
cd dado-claude-toolkit
git log --oneline -5          # what you are getting
claude plugin validate .
python tests/run_validation.py
python tests/run_hook_commands.py
```

Then read the four hook scripts. They are the only code that executes:

```
plugins/dado-core/hooks/guard_secret_files.py
plugins/dado-release-safety/hooks/guard_destructive_commands.py
plugins/dado-release-safety/hooks/guard_protected_branch.py
plugins/dado-release-safety/hooks/remind_uncommitted.py
```

Each is under 200 lines, standard library only, and documents its own limits at the
top.
