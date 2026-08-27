# Install

## Before you install anything

A Claude Code plugin executes with your privileges. Installing one from a marketplace
is a trust decision, not a convenience. Read
[TRUST-AND-PERMISSIONS.md](TRUST-AND-PERMISSIONS.md) first.

Check that you are installing from the expected owner and repository:

```
Owner:      Dado211207
Repository: Dado211207/dado-claude-toolkit
Marketplace name: dado-tools
Version:    0.1.0
```

A marketplace with the same name from a different repository is a different thing.

## 1. Add the marketplace

From your shell:

```bash
claude plugin marketplace add Dado211207/dado-claude-toolkit
```

Or inside a Claude Code session:

```
/plugin marketplace add Dado211207/dado-claude-toolkit
```

Adding a marketplace **installs nothing**. It registers the catalogue so you can see
what is in it.

To pin to a specific ref instead of tracking the default branch, append `@<ref>`:

```bash
claude plugin marketplace add Dado211207/dado-claude-toolkit@<tag-branch-or-sha>
```

No tag exists for 0.1.0 at the time of writing. Pin to a commit SHA if you want
content that cannot change under you.

## 2. See what is in it

```
/plugin
```

Open the **Discover** tab. Each plugin's detail view lists the skills, agents and
hooks it will add, and its context cost, before you install it. Read that list.

Or from the shell:

```bash
claude plugin marketplace list
```

## 3. Install only what you need

```bash
claude plugin install dado-core@dado-tools
claude plugin install dado-web-quality@dado-tools
claude plugin install dado-python-windows@dado-tools
claude plugin install dado-content-localization@dado-tools
claude plugin install dado-release-safety@dado-tools
```

Install the ones your project actually uses. Every enabled plugin costs context on
every turn. The [adoption profiles](../profiles/) say which combination fits which
kind of project.

Inside a session, the same commands work with a leading slash:

```
/plugin install dado-core@dado-tools
```

### Scopes

`claude plugin install` installs to **user** scope by default. Use `--scope` to
choose:

```bash
claude plugin install dado-core@dado-tools --scope project   # everyone on this repo
claude plugin install dado-core@dado-tools --scope local     # just you, just this repo
```

- **user** — you, in every project
- **project** — written to the repository's `.claude/settings.json`, shared with
  everyone who clones it
- **local** — you, in this repository only, not shared

## 4. Confirm the trust prompt yourself

Claude Code shows a workspace-trust dialog for a repository whose settings file
grants capability. It lists what the folder would grant. **Read it before accepting.**

This toolkit's profiles ship `deny` rules only, so there is nothing to grant — but
confirm the dialog yourself rather than clicking through it, every time, for every
repository.

## 5. Verify what is enabled

```bash
claude plugin list
```

Or in a session, `/plugin` → **Installed**. Check that the plugins listed are the
ones you meant to install, from the marketplace you meant.

If the install summary says `Run /reload-plugins to activate.`, run that. If it warns
that the reload will re-read the conversation, rerun it as `/reload-plugins --force`.

## 6. Use the skills

Plugin skills are namespaced:

```
/dado-core:orient
/dado-core:verify-and-report
/dado-web-quality:web-audit
/dado-python-windows:packaging-verify
/dado-content-localization:bilingual-sync
/dado-release-safety:deploy-gate
```

Claude can also load them on its own when a task matches a skill's description, with
one exception: `/dado-release-safety:draft-pr` sets `disable-model-invocation: true`,
so only you can start it.

Agents are referenced by their scoped name, for example
`dado-core:final-verifier` or `dado-release-safety:release-gatekeeper`.

## Adopting it in a project

Committing the marketplace declaration means everyone on the repository sees it:

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

Copy this from the profile that fits your project rather than typing it. Note that a
committed declaration is **not** an install: each person still trusts the folder, and
may still need to run `claude plugin install` once. See
[CLAUDE-CODE-COMPATIBILITY.md](CLAUDE-CODE-COMPATIBILITY.md#the-cloud-caveat-stated-honestly).

## Requirements

| Requirement | For | If absent |
| --- | --- | --- |
| A Claude Code version with `/plugin` | Everything | Update; `claude --version` reports yours |
| `git` | Every git-state check | The workflow does not apply |
| Python 3 as `python` on `PATH` | The four hooks, and the validation suite | The hooks are inert. Skills still work |

No dependency is added to your project.

## Verify the toolkit itself

Clone it and check it before or after installing:

```bash
git clone https://github.com/Dado211207/dado-claude-toolkit
cd dado-claude-toolkit
claude plugin validate .
python tests/run_validation.py
python tests/run_hook_commands.py
```

The second command runs 30 structural, safety and behavioural checks, including the
ones that prove no plugin ships an `allow` rule and no hook can grant a permission.

## Uninstalling

See [UNINSTALL.md](UNINSTALL.md).
