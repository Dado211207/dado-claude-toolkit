# Troubleshooting

## `/plugin` is not recognised

You are in a Claude Code on the web session, where `/plugin` is a terminal-only
command, or your CLI predates plugin support.

- Cloud: see [CLOUD-USAGE.md](CLOUD-USAGE.md).
- CLI: `claude --version`, then update.

## The marketplace was added but no skills appear

In order:

1. `claude plugin list` — is the plugin installed, or only the marketplace added?
   Adding a marketplace installs nothing.
2. Did the install summary say `Run /reload-plugins to activate.`? Run it
   (`--force` if it warns about the prompt cache).
3. `/plugin` → **Errors** tab.
4. Clear the cache and restart: `rm -rf ~/.claude/plugins/cache`.
5. Accept the workspace-trust prompt if it is waiting.

## A project's `.claude/settings.json` enables a plugin but it does not load

Expected in some versions. A plugin from an external source that only project
settings enable does not load until someone installs it once:

```bash
claude plugin install dado-core@dado-tools
```

Background: [CLAUDE-CODE-COMPATIBILITY.md](CLAUDE-CODE-COMPATIBILITY.md#the-cloud-caveat-stated-honestly).

## The hooks do nothing

They need Python 3 exposed as `python` on `PATH`. When it is missing, the hook command fails, Claude
Code treats that as non-blocking, and the guard is silently inert — no error, no
protection.

```bash
python --version
```

On Windows, ensure `python --version` resolves to Python 3. The repository's native
Windows CI executes the exact commands from both `hooks.json` files.
Also check the plugin is enabled (`claude plugin list`) and that
`disableAllHooks` is not set in any settings file.

The skills do not depend on the hooks.

## A hook is blocking something I actually want

- **`.env` or a key file refused** — that is the secret guard. If the file is a
  documented placeholder, rename it to a `.example` form. Otherwise write it
  yourself, outside the session.
- **A git or deploy command needs confirming** — that is `escalate`, and approving
  the prompt is the intended path.
- **Editing on `main` keeps prompting** — set `DADO_PROTECTED_BRANCHES` to your real
  list, or work on a feature branch.
- **Turn them off**: `/plugin disable dado-release-safety@dado-tools`, or
  `"disableAllHooks": true` (which disables *every* hook, from every source).

## The validation suite fails

```bash
python tests/run_validation.py
python tests/run_hook_commands.py
```

Each failing check prints the exact file, line and reason. Common causes:

| Message | Cause |
| --- | --- |
| `does not end with a newline` / `contains CRLF` | An editor rewrote the file. Check `.gitattributes` is respected |
| `broken relative link` | A doc points at a path that does not exist |
| `references unknown skill or agent` | A README or doc names a skill that was renamed or removed |
| `does not document /plugin:skill` | A new skill was added without a README row |
| `ships a permissions.allow rule` | Something added a grant. This toolkit ships deny rules only |
| `check raised …` | A check itself is broken — that is a failure, not a pass |

`--quick` skips the subprocess-based checks (24 and 25) and reports them as
**skipped**, not passed.

## `claude plugin validate` is not available

The CLI is not installed in this environment. Say so in your report — the structural
suite is not a substitute for the official validator, and neither is a substitute for
the other. The CI workflow reports it as skipped when the CLI is absent rather than
claiming it passed.

## A skill is not being picked up automatically

Claude loads a skill when the task matches its `description`. Invoke it explicitly
with `/plugin-name:skill-name`. One skill never auto-loads by design:
`/dado-release-safety:draft-pr` sets `disable-model-invocation: true`.

## Sessions feel slower or context fills faster

Every enabled plugin costs context on every turn. Disable the ones this project does
not use:

```bash
claude plugin disable dado-web-quality@dado-tools
```

`/plugin` → **Installed** shows what is enabled and flags plugins you have not used
recently.

## Something else

Open an issue at `https://github.com/Dado211207/dado-claude-toolkit/issues` with the
output of `claude --version`, `claude plugin list`, and
`python tests/run_validation.py`. Do not paste credentials.
