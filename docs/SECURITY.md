# Security

What this toolkit guards, what it does not, and how to report a problem.

For the trust model and permission design, see
[TRUST-AND-PERMISSIONS.md](TRUST-AND-PERMISSIONS.md). For the attacker-by-attacker
analysis, see [THREAT-MODEL.md](THREAT-MODEL.md).

## Rules this repository holds itself to

1. **No secrets, ever.** No credential, token, key, cookie or connection string in
   any tracked file, fixture, log or document. Checks 12 and 13 fail the build on a
   match; the patterns are built from split literals so the scanner does not report
   itself, and no secret-shaped fixture is committed — the rejection cases are
   generated into a temp directory at test time.
2. **No permission grants.** Zero `allow` rules, zero `allowed-tools`, zero MCP
   servers, zero hooks that emit `allow`. Enforced by checks 14, 15, 16, 24 and 27.
3. **No dependencies.** Standard library and `git` only. Check 26 fails if a
   manifest, lockfile or non-stdlib import appears.
4. **Hooks are read-only.** No file writes, no network, no shell, no destructive
   command, no credential access, no telemetry. Check 29 greps the hook sources for
   `urllib`, `requests`, `socket`, write-mode `open`, `shutil` mutations, `os.remove`
   and `shell=True`. Check 24 proves at runtime that running every hook against
   eleven payloads plus seven malformed inputs changes not one byte in the repository
   or in the temp directory.
5. **No absolute personal paths.** Check 11.
6. **Nothing silently enables a merge, release or deployment.** Checks 15 and 16.
7. **No access to unrelated repositories.** Check 17 fails on a reference to the
   excluded private desktop-assistant repository.

## What the hooks actually do

| Hook | Event | Decision | Never |
| --- | --- | --- | --- |
| `guard_secret_files.py` | `PreToolUse` on Write/Edit | `deny` for private keys, keystores, `.env` with values, credential directories, PEM key content; `escalate` for `.npmrc`/`.pypirc`/`.netrc` and token-shaped content | `allow` |
| `guard_destructive_commands.py` | `PreToolUse` on Bash | `escalate` for force push, ref deletion, hard reset, `git clean -f`, history rewrite, reflog expiry, stash drop, amend, `git merge`, `gh pr merge`, release/repo changes, package publish, host deploys, `rm -rf` | `allow`, `deny` |
| `guard_protected_branch.py` | `PreToolUse` on Write/Edit | `escalate` when the checkout is on a protected branch | `allow`, `deny` |
| `remind_uncommitted.py` | `Stop` | Advisory `systemMessage` only | any decision |

`escalate` forces **your** permission prompt to appear. It cannot approve anything.

Two hooks run read-only `git` subcommands (`rev-parse`, `status --porcelain`) with no
shell, a five-second cap, in the session's working directory. Nothing else executes.

## Limits, stated plainly

- **The hooks are not a security boundary.** They match text, they can be disabled,
  and they are inert without Python 3 exposed as `python`. Do not use them to contain an untrusted
  agent.
- **The validation suite checks this repository, not your project.** It proves the
  toolkit ships nothing dangerous. It says nothing about the code you point it at.
- **A skill is an instruction, not a control.** It shapes behaviour; it does not
  enforce it. The enforcement points are Claude Code's permission system, your deny
  rules, and your git host's branch protection.
- **Public visibility does not make code safe.** Read it.

## Dependencies

**None.** No `package.json`, no `requirements.txt`, no lockfile, no MCP server.

Should a future version propose one, it must document, in the pull request: exact
name, exact version, licence, purpose, installation impact, supply-chain risk, and
why the standard library is insufficient. Adding a dependency to a toolkit whose
value is being auditable needs to clear a high bar.

## If you find a security problem

Open an issue at
`https://github.com/Dado211207/dado-claude-toolkit/issues` describing what you found
and how to reproduce it.

**Do not include a real credential in the report.** If a secret is exposed, say where
it is, not what it is — and assume it is already compromised and rotate it.
