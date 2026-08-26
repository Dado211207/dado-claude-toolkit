# dado-core

Shared working discipline for any repository: orient before editing, plan before
changing, debug from evidence, edit without collateral damage, pick the right
checks, and report honestly.

- **Version:** 0.1.0
- **Marketplace:** `dado-tools`
- **Install:** `/plugin install dado-core@dado-tools`
- **Depends on:** nothing. Every other dado-tools plugin is useful on its own, but
  they assume the honesty rules that live here. Installing `dado-core` alongside
  them is recommended, not required.

## Skills

| Skill | Invoke | What it does |
| --- | --- | --- |
| Orient | `/dado-core:orient` | Read repository rules, identify the stack from manifests, capture git state, list protected areas |
| Plan a change | `/dado-core:plan-change` | Scope in/out/unknown, baseline capture, verifiable steps, an explicit stop line |
| Evidence-first debugging | `/dado-core:debug-evidence` | Reproduce, isolate, classify, fix the cause, prove it both directions |
| Safe editing | `/dado-core:safe-edit` | Preserve unrelated user changes, minimal diffs, never hand-edit generated files |
| Test selection | `/dado-core:select-tests` | Match checks to blast radius using the project's own commands; know what each proves |
| Final verification | `/dado-core:verify-and-report` | Re-run checks, print git identity, report skips and unknowns |
| Project state | `/dado-core:project-state` | Read and maintain an optional tracked `docs/ai/PROJECT_STATE.md` |
| Uncertainty log | `/dado-core:uncertainty-log` | Keep fact, inference and assumption labelled all the way to the report |

Claude can also load these automatically when a task matches the description.

## Agents

| Agent | Tools | Responsibility |
| --- | --- | --- |
| `dado-core:repository-auditor` | Read, Grep, Glob, Bash | Read-only orientation report |
| `dado-core:implementation-reviewer` | Read, Grep, Glob, Bash | Review a diff for correctness, scope creep, collateral damage |
| `dado-core:test-investigator` | Read, Grep, Glob, Bash | Find why a check fails and classify it |
| `dado-core:security-reviewer` | Read, Grep, Glob, Bash | Injection, secret exposure, path handling, permission widening |
| `dado-core:final-verifier` | Read, Grep, Glob, Bash | Independent re-run and git-identity check before handing back |

Each agent has a narrow brief and a restricted tool list. None of them can spawn
further agents: the `Agent` tool is not in any of their allowlists.

## Hook

One hook, `PreToolUse` on `Write`, `Edit` and `NotebookEdit`:
`hooks/guard_secret_files.py` refuses writes whose target is obvious secret
material (private keys, keystores, `.env` files with real values, credential
directories) and asks for confirmation on files that commonly hold a token
(`.npmrc`, `.pypirc`, `.netrc`) or on content shaped like a provider API token.

What it does **not** do, stated plainly:

- It is **not a security boundary.** It sees only tool calls Claude Code routes
  through it, and the user can turn it off at any time.
- It never emits `allow`. It can only refuse or ask, never grant. When nothing
  matches it prints nothing and the normal permission flow applies unchanged.
- It writes no files, makes no network call, and reads no environment variable.
- It requires `python3` on `PATH`. Without it the hook fails and Claude Code treats
  that as non-blocking, so the guard silently does nothing. On Windows, ensure
  `python3` resolves (the `py` launcher aliases usually provide it) or expect the
  hook to be inert.

To turn it off without uninstalling the plugin, set `"disableAllHooks": true` in
your settings (this disables *all* hooks, not just this one), or disable the plugin
with `/plugin disable dado-core@dado-tools`.

## The honesty rules

`reference/honesty-rules.md` is the shared rule set the skills point at. The short
version:

1. A check that did not run did not pass.
2. Name the outcome class: product-defect, test-defect, environment, flaky, not-run.
3. Never widen a limit to make red go green.
4. Keep fact, inference and assumption separate.
5. Report what you did not do.
6. No hardware, no hardware claim.
7. Print the SHA before claiming a git state.

## Uninstall

```
/plugin uninstall dado-core@dado-tools
```

Nothing is left behind in your repository: this plugin creates no files. If you
adopted `docs/ai/PROJECT_STATE.md`, that file is yours and stays until you delete it.
