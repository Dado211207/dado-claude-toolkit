# dado-claude-toolkit

A Claude Code **plugin marketplace** named `dado-tools`, containing five opt-in
plugins for repository discipline, web quality, Python/Windows desktop releases,
bilingual content review, and release safety.

- **Version:** 0.1.0 (initial MVP)
- **Owner:** [Dado211207](https://github.com/Dado211207)
- **Repository:** `Dado211207/dado-claude-toolkit`
- **Marketplace name:** `dado-tools`
- **Dependencies:** none. Standard library and `git` only.

> **Not affiliated with Anthropic.** This is a personal toolkit that uses Claude
> Code's documented plugin, skill, agent and hook formats. It is not endorsed by,
> supported by, or connected to Anthropic in any way.

## What it is

A set of reusable instructions — skills, narrowly scoped agents, and four small
safety hooks — that make Claude Code's work in a repository more consistent and its
reports harder to fake.

## What it is not

- **Not a way to give Claude more access.** It ships **zero** `permissions.allow`
  rules, zero `allowed-tools` grants, and zero MCP servers. Its hooks can only
  *refuse* or *ask* — they never emit `allow`.
- **Not unrestricted or unlimited Claude access.** Nothing here removes a permission
  prompt, and nothing here bypasses Claude Code's permission system.
- **Not a security boundary.** The hooks are convenience guards. They see only what
  Claude Code routes through them, a user can disable them, and they are inert
  without `python3`.
- **Not memory.** `docs/ai/PROJECT_STATE.md` is an ordinary tracked file, read again
  because it is committed. Claude Code carries no state between sessions on its own.
- **Not "globally enabled everywhere".** Installation is per scope, and cloud
  sessions have real limits — see [docs/CLOUD-USAGE.md](docs/CLOUD-USAGE.md).

## Plugins

| Plugin | Version | What it covers |
| --- | --- | --- |
| [`dado-core`](plugins/dado-core/) | 0.1.0 | Orientation, planning, evidence-first debugging, safe editing, test selection, honest verification, uncertainty tracking, optional project state |
| [`dado-web-quality`](plugins/dado-web-quality/) | 0.1.0 | Responsive layout, accessibility, routing and scroll behaviour, metadata and SEO, security/caching headers, browser testing, deploy previews |
| [`dado-python-windows`](plugins/dado-python-windows/) | 0.1.0 | Windows code review, PyInstaller and Inno Setup verification, installer lifecycle, devices and credentials, Windows CI portability |
| [`dado-content-localization`](plugins/dado-content-localization/) | 0.1.0 | Factual claims, EN/ME parity, CV consistency, copy quality, content diffs |
| [`dado-release-safety`](plugins/dado-release-safety/) | 0.1.0 | Pre-change snapshot, CI evidence, artifact integrity, Draft PR, deploy gate |

31 skills, 14 agents, 4 hooks. Each plugin works on its own; installing `dado-core`
alongside the others is recommended, not required.

## Trust warning — read before installing

A Claude Code plugin executes with your privileges. Anthropic does not verify
third-party plugins.

- Install only from `Dado211207/dado-claude-toolkit`. A marketplace with the same
  name from another repository is a different thing.
- Read the diff before updating. Pin to a commit SHA if you want content that cannot
  change under you.
- **Public visibility does not make code safe.** Being able to read it is not the
  same as having read it.
- Confirm the workspace-trust prompt yourself, every time.

See [docs/TRUST-AND-PERMISSIONS.md](docs/TRUST-AND-PERMISSIONS.md) and
[docs/SECURITY.md](docs/SECURITY.md).

## Install

```bash
claude plugin marketplace add Dado211207/dado-claude-toolkit
claude plugin install dado-core@dado-tools
```

Adding a marketplace installs nothing; it registers the catalogue. Install only the
plugins you need — every enabled plugin costs context on every turn. Full
instructions, scopes and pinning: [docs/INSTALL.md](docs/INSTALL.md).

## Example usage

```
/dado-core:orient                        # before changing anything
/dado-core:verify-and-report             # before handing work back
/dado-web-quality:web-audit              # what can honestly be checked here
/dado-release-safety:deploy-gate         # the stop line before anything irreversible
```

Claude can also load a skill on its own when the task matches its description. The
one exception is `/dado-release-safety:draft-pr`, which only you can start.

## Cloud limitations, in one paragraph

`/plugin` is a terminal-only command and is **not available in Claude Code on the
web**. The documented cloud path is declaring the marketplace and plugins in a
committed `.claude/settings.json` — but the same documentation notes that a plugin
from an external source may not load until someone installs it once. This repository
has **not** verified that end to end. What always works in a cloud session is
committed repository content: `.claude/agents/`, `.claude/skills/`, `CLAUDE.md`, and
`permissions.deny`. See [docs/CLOUD-USAGE.md](docs/CLOUD-USAGE.md) for the fallbacks.

## Update

```bash
claude plugin marketplace update dado-tools
```

Review what changed before you accept it — see [docs/MAINTENANCE.md](docs/MAINTENANCE.md).

## Uninstall

```bash
claude plugin uninstall dado-core@dado-tools
claude plugin marketplace remove dado-tools
```

No plugin writes files into your repository, so nothing is left behind. Full list of
what to clean up: [docs/UNINSTALL.md](docs/UNINSTALL.md).

## Validate

```bash
claude plugin validate .              # the official Claude Code validator
python3 tests/run_validation.py       # 30 structural, safety and behavioural checks
```

The suite uses the Python standard library only and needs no network access. It
proves, among other things, that no plugin ships an `allow` rule, no hook can grant a
permission, no secret or private key is committed, and no plugin enables a merge or a
deployment.

## Adoption profiles

Five worked examples in [`profiles/`](profiles/): minimal, React/Vite/Netlify,
Python/Windows desktop, bilingual content site, and release-sensitive. Each has a
`settings.json` and a `CLAUDE.md` snippet to copy and edit. Nothing installs itself.

## Documentation

| Document | What is in it |
| --- | --- |
| [INSTALL](docs/INSTALL.md) / [UNINSTALL](docs/UNINSTALL.md) | Install, scopes, pinning, clean removal |
| [LOCAL-USAGE](docs/LOCAL-USAGE.md) / [CLOUD-USAGE](docs/CLOUD-USAGE.md) | CLI and Desktop; web sessions and their limits |
| [GITHUB-ACTIONS](docs/GITHUB-ACTIONS.md) | Using the plugins in a workflow |
| [ADOPTION](docs/ADOPTION.md) | Which profile fits which project |
| [CLAUDE-CODE-COMPATIBILITY](docs/CLAUDE-CODE-COMPATIBILITY.md) | Formats used, sources, and the support matrix |
| [SECURITY](docs/SECURITY.md) / [THREAT-MODEL](docs/THREAT-MODEL.md) / [TRUST-AND-PERMISSIONS](docs/TRUST-AND-PERMISSIONS.md) | What is guarded, what is not, and who decides |
| [MAINTENANCE](docs/MAINTENANCE.md) | Updating, re-verifying, and the future-work list |
| [TROUBLESHOOTING](docs/TROUBLESHOOTING.md) | When something does not load |

## Licence

MIT. See [LICENSE](LICENSE).
