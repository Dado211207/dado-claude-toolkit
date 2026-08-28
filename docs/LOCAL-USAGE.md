# Local usage — CLI and Desktop

Everything in the toolkit works in the Claude Code CLI. The Desktop app supports the
same plugins through its plugin browser instead of the `/plugin` panel.

Install steps are in [INSTALL.md](INSTALL.md). This page is what to do afterwards.

## A normal session

```
/dado-core:orient                  # read the rules, identify the stack, capture git state
… do the work …
/dado-core:verify-and-report       # re-run the checks, print the git identity, report honestly
```

Claude loads a skill on its own when the task matches its description, so you often
do not need to type one. Invoke explicitly when you want a specific discipline
applied, or when Claude did not pick it up.

## Skills by situation

| Situation | Skill |
| --- | --- |
| New repository, unclear rules | `/dado-core:orient` |
| Multi-file or risky change | `/dado-core:plan-change` |
| Something fails | `/dado-core:debug-evidence` |
| Deciding what to run | `/dado-core:select-tests` |
| Before handing back | `/dado-core:verify-and-report` |
| Reviewing a site | `/dado-web-quality:web-audit` first, then what it points at |
| Choosing or refining a UI direction | `/dado-ui-design:ui-ux-pro-max` |
| A browser test is red | `/dado-web-quality:browser-testing` |
| Windows packaging | `/dado-python-windows:packaging-verify` |
| Installer behaviour | `/dado-python-windows:install-lifecycle-test` |
| Editing bilingual content | `/dado-content-localization:bilingual-sync` |
| After any content edit | `/dado-content-localization:content-diff-review` |
| Before opening a PR | `/dado-release-safety:draft-pr` |
| Anything approaching a deploy | `/dado-release-safety:deploy-gate` |

## Agents

Reference an agent by its scoped name, or @-mention it:

```
Use the dado-core:final-verifier agent before you report this done.
Use dado-release-safety:release-gatekeeper to tell me whether this is ready to propose.
```

Agents run in their own context, so they keep a long review out of your main
conversation. Each has a restricted tool list and none can spawn further agents.

## Hooks you will notice

With `dado-core` installed, a write to a `.env` file, a private key or a credential
directory is refused with a reason. With `dado-release-safety` installed, a force
push, a `git merge`, a `gh pr merge`, a package publish, a host deploy or an `rm -rf`
brings up **your** permission prompt instead of running, and editing a file while on
`main` does the same.

Change the protected branch list with an environment variable:

```bash
export DADO_PROTECTED_BRANCHES="main,release,production"
```

To silence all hooks: `"disableAllHooks": true` in settings, or disable the plugin.

## Development against a local checkout

Testing a change to the toolkit itself, without installing it:

```bash
claude --plugin-dir ./plugins/dado-core
claude --plugin-dir ./plugins/dado-core --plugin-dir ./plugins/dado-release-safety
```

A `--plugin-dir` plugin takes precedence over an installed one of the same name for
that session. After editing, `/reload-plugins` (or `/reload-plugins --force` if it
warns about the prompt cache).

## Keeping context cost down

Every enabled plugin adds to the context window on every turn. Install the ones the
project uses, not all six. `/plugin` → **Installed** shows what is enabled and
flags plugins you have not used recently.
