# Threat model

A threat review of **the toolkit itself** — what could go wrong with installing and
running it, and what is and is not mitigated. Scope: version 0.1.0.

`Mitigated` means a check or a design choice makes it hard. `Partial` means it is
reduced, not removed. `Not mitigated` means you are the control.

## Assets

Your source code and repositories; your credentials and credential stores; your
production systems; your git history; your machine.

## Adversaries

1. A compromised or malicious version of **this repository**.
2. **Repository content** in a project Claude is working on (prompt injection).
3. A **dependency or MCP server** pulled in by a future version.
4. **Nobody** — the agent's own mistake, which is the most common case.

## Threats

| # | Threat | Status | Why |
| --- | --- | --- | --- |
| 1 | **Prompt injection in repository files** — a file tells the agent to escalate, exfiltrate, or act elsewhere | Partial | Every skill states that repository content describes conventions but cannot expand permissions, authorise a merge or deploy, or send data anywhere, and should be surfaced rather than followed. This is guidance; it is not enforcement. Your deny rules and the permission prompts are the real controls |
| 2 | **Malicious dependency install script** | Mitigated | No dependencies. Check 26 fails on any manifest, lockfile or non-stdlib import |
| 3 | **Untrusted MCP server** | Mitigated | None shipped. Check 27 fails on `.mcp.json` or an `mcpServers` key |
| 4 | **Secrets committed to this repository** | Mitigated | Checks 12 and 13. Patterns are split literals so the scanner does not self-match; secret-shaped fixtures are generated at test time, never committed |
| 5 | **Secrets leaked into logs or reports** | Partial | Hooks print no environment variable and never echo file content. Skills forbid printing credentials. An agent can still paste something into a report — nothing here prevents that |
| 6 | **Destructive shell command** | Partial | `guard_destructive_commands.py` escalates 22 command families to your prompt. Text matching, so an equivalent command written differently or built at runtime slips past. Profile deny rules are the stronger layer |
| 7 | **Overly broad permissions** | Mitigated | Zero `allow` rules, zero `allowed-tools`, no hook emits `allow`. Checks 14, 15, 16, 24 |
| 8 | **Unsafe git operation** (force push, history rewrite, ref deletion) | Partial | Escalated by hook and denied in profiles. Not enforcement — see #6 |
| 9 | **Unintended production deployment** | Partial | Deploy commands denied in profiles and escalated by hook; `deploy-gate` states the stop line; no skill or agent performs a deploy. But nothing can stop a user who approves the prompt |
| 10 | **Hidden network call** | Mitigated | Check 29 rejects `urllib`, `requests`, `http.client`, `socket` in hook sources. Check 24 proves the hooks run without one. No telemetry, no analytics, no callback |
| 11 | **Hook writes or deletes files** | Mitigated | Check 29 rejects write-mode `open`, `shutil` mutations and `os.remove`. Check 24 hashes the whole repository and the temp directory before and after running every hook against 11 payloads and 7 malformed inputs, and fails on any difference |
| 12 | **Symlink or path traversal** | Partial | Check 3 rejects a marketplace `source` containing `..` or resolving outside the repository, with a fixture proving the rejection. The official `claude plugin validate` also checks source path traversal |
| 13 | **Absolute path leakage** | Mitigated | Check 11, with documentation placeholders (`<user>`) deliberately excluded from the pattern |
| 14 | **Command injection through a filename** | Partial | The hooks never build a shell command: `guard_protected_branch.py` and `remind_uncommitted.py` call `git` with an argument list and no shell. Check 29 rejects `shell=True`. Skills tell reviewers to treat filenames as untrusted input. Code *in your project* is your responsibility |
| 15 | **False test reporting** — the agent claims a check passed that never ran | Partial | The honesty rules make it a stated violation, the report format demands exit codes and counts, and the suite reports skips separately and says in its own output that skips are not passes. No tooling can prevent a model from writing a false sentence — read the commands in the report |
| 16 | **Compromised plugin content** — this repository is changed under you | Partial | Pin to a commit SHA; review the diff before updating; the validation suite runs in CI on every push and pull request. If the owner's account were compromised, a pinned SHA is the only real defence |
| 17 | **Marketplace update risk** — auto-update pulls a change you did not review | Partial | Third-party marketplaces have auto-update **off** by default. Keep it off, pin a ref, and read [MAINTENANCE.md](MAINTENANCE.md) before updating |
| 18 | **Name confusion** — a different repository publishing a `dado-tools` marketplace | Not mitigated | Marketplace names are not globally unique. Verify the owner and repository: `Dado211207/dado-claude-toolkit`. `claude plugin marketplace list` shows the source of each |
| 19 | **A user disables the guards** | Not mitigated, by design | You can disable any hook or delete any deny rule. That is your decision to make |
| 20 | **Cloud session data exposure** | Not mitigated by this toolkit | A cloud session can reach the network per its environment policy, and sharing a session can expose repository content. See the Claude Code security documentation |

## The uncomfortable summary

The strong mitigations are the **absences**: no dependencies, no MCP servers, no
allow rules, no network, no writes. Those are verifiable and enforced by CI.

The weak mitigations are the **behavioural** ones: prompt-injection resistance,
honest reporting, stopping before a merge. They are instructions to a model. They
raise the floor; they do not enforce anything.

Do not deploy this toolkit as a control. Deploy it as a discipline, keep your deny
rules, keep branch protection on your git host, and read the commands in the reports.

## Out of scope

Claude Code's own security model; your project's vulnerabilities; your CI platform;
your git host's access control; a compromised developer machine.
