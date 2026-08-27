# Claude Code compatibility

What this toolkit relies on, where each part works, and where it does not.

**Researched against the official Anthropic documentation on 2026-08-26, with the
Claude Code CLI at version 2.1.246.** Claude Code changes quickly. Re-read the
sources below before trusting any claim on this page, and see
[MAINTENANCE.md](MAINTENANCE.md) for how to re-verify it.

## Documentation sources

| Topic | URL |
| --- | --- |
| Plugin marketplaces | https://code.claude.com/docs/en/plugin-marketplaces |
| Creating plugins | https://code.claude.com/docs/en/plugins |
| Plugins reference (schemas, paths, variables) | https://code.claude.com/docs/en/plugins-reference |
| Discovering and installing plugins | https://code.claude.com/docs/en/discover-plugins |
| Skills | https://code.claude.com/docs/en/skills |
| Subagents | https://code.claude.com/docs/en/sub-agents |
| Hooks | https://code.claude.com/docs/en/hooks |
| Settings | https://code.claude.com/docs/en/settings |
| Settings reference | https://code.claude.com/docs/en/settings-reference |
| Permissions | https://code.claude.com/docs/en/permissions |
| Claude Code on the web | https://code.claude.com/docs/en/claude-code-on-the-web |
| Cloud environments | https://code.claude.com/docs/en/cloud-environments |
| GitHub Actions | https://code.claude.com/docs/en/github-actions |
| Settings JSON schema | https://json.schemastore.org/claude-code-settings.json |
| Marketplace JSON schema | https://json.schemastore.org/claude-code-marketplace.json |

Both schema URLs returned HTTP 200 when checked. There is no published
`claude-code-plugin.json` schema, so `plugin.json` files here carry no `$schema` key.

## Formats this toolkit uses

Only fields the official documentation defines. No invented keys.

### Marketplace — `.claude-plugin/marketplace.json`

Required: `name`, `owner` (an object with `name`), `plugins` (array).
Each plugin entry requires `name` and `source`.

Also used here: `$schema`, `description`, `version`, and per entry `displayName`,
`description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`,
`category`. All are documented optional fields.

`source` is a relative path string (`"./plugins/dado-core"`), which is the documented
form for plugins living in the same repository as the marketplace.

### Plugin — `<plugin>/.claude-plugin/plugin.json`

Only `name` is required. This toolkit also sets `displayName`, `version`,
`description`, `author`, `homepage`, `repository`, `license`, `keywords`.

Components live at the **plugin root**, never inside `.claude-plugin/`:
`skills/<name>/SKILL.md`, `agents/*.md`, `hooks/hooks.json`. Because these are the
documented default locations, no `skills`, `agents` or `hooks` path field is set in
any manifest.

### Skills — `skills/<name>/SKILL.md`

YAML front-matter with `name` and `description`.
`disable-model-invocation: true` is used on exactly one skill
(`dado-release-safety:draft-pr`), so a pull request is only ever opened when you ask.

Invocation for a plugin skill is `/<plugin-name>:<skill-name>`.

**No skill in this toolkit sets `allowed-tools`.** That field pre-approves tools for
the turn that invokes the skill, which is a permission grant. Version 0.1.0 grants
nothing; check 14 of the validation suite fails the build if any skill adds it.

### Agents — `agents/<name>.md`

YAML front-matter with `name` and `description` required; `tools` and `color` used
here. `tools` is an allowlist, so naming a short list **restricts** an agent rather
than granting it anything.

No agent lists `Agent` in `tools`, so none of them can spawn further agents. Check 8
enforces this.

Plugin agents **ignore** `hooks`, `mcpServers` and `permissionMode`. Shipping those
fields would imply behaviour that does not happen, so check 8 fails the build if one
appears.

Plugin agents are referenced as `<plugin-name>:<agent-name>`.

### Hooks — `hooks/hooks.json`

```json
{ "hooks": { "<Event>": [ { "matcher": "<ToolName>", "hooks": [ { "type": "command", "command": "…", "timeout": 15 } ] } ] } }
```

All four hook scripts are invoked as
`python "${CLAUDE_PLUGIN_ROOT}/hooks/<script>.py"`. `${CLAUDE_PLUGIN_ROOT}` is the
documented substitution for a plugin's install directory.

The destructive-command group matches both `Bash` and `PowerShell`. Its bounded
PowerShell coverage includes the direct recursive-force `Remove-Item` forms; text
assembled at runtime or hidden in a script remains outside this convenience guard.

Decisions returned: `deny` and `escalate` only. **Never `allow`** — emitting `allow`
from a hook suppresses your own permission prompt, which would convert a safety hook
into a permission grant. Checks 15 and 24 enforce this statically and at runtime.

### Settings — `.claude/settings.json`

`extraKnownMarketplaces` maps a marketplace name to a source:

```json
{ "extraKnownMarketplaces": { "dado-tools": { "source": { "source": "github", "repo": "Dado211207/dado-claude-toolkit" } } } }
```

`enabledPlugins` maps `plugin@marketplace` to a boolean:

```json
{ "enabledPlugins": { "dado-core@dado-tools": true } }
```

Both key shapes are confirmed against the published settings JSON schema.

## Where each part works

| Capability | CLI | Desktop | Web / cloud | GitHub Actions |
| --- | --- | --- | --- | --- |
| `/plugin` interactive manager | Yes | Plugin browser in the app | **No** — terminal-only command | No |
| `claude plugin …` shell commands | Yes | Via a terminal | Not applicable | No |
| Marketplace from `extraKnownMarketplaces` | Yes, after trust | Yes, after trust | Yes, after trust — see the caveat below | Use `plugin_marketplaces` input |
| Plugins from `enabledPlugins` | Yes | Yes | Documented path for cloud — see caveat | Use `plugins` input |
| Plugin skills (`/plugin:skill`) | Yes | Yes | Yes, once the plugin loads | Yes, as the `prompt` |
| Plugin agents | Yes | Yes | Yes | Yes |
| Repository `.claude/agents/` | Yes | Yes | **Yes — picked up automatically** | Yes, after checkout |
| Repository `.claude/skills/` | Yes | Yes | Yes | Yes, after checkout |
| Hooks from a plugin | Yes | Yes | Yes, if the plugin loads and `python` resolves to Python 3 | Linux and Windows commands exercised in this repository's CI |
| `permissions.deny` from project settings | Immediately | Immediately | Immediately | Via the `settings` input |
| `permissions.allow` from project settings | **After you trust the folder** | After trust | After trust | Via the `settings` input |

### The cloud caveat, stated honestly

Two official statements are both true and sit in tension:

1. *Discover and install plugins* says: "If Claude replies that `/plugin` isn't
   available in this environment, use the plugin browser in the Claude desktop app,
   or declare the plugin under `enabledPlugins` in `.claude/settings.json` for cloud
   sessions."

2. The same page says: "As of Claude Code v2.1.195, adding the marketplace doesn't
   install plugins that come from an external source, on any path that loads plugins.
   A plugin that only the project's `.claude/settings.json` enables, and that comes
   from an external source such as a GitHub repository or npm package, doesn't load
   until the team member installs it."

This toolkit's plugins come from a GitHub repository, which is an external source. So
`enabledPlugins` in a committed settings file is the documented cloud path, **and**
the second statement says such a plugin may report as not installed until someone
installs it once.

**This has not been verified end-to-end in a cloud session by this repository.** See
[CLOUD-USAGE.md](CLOUD-USAGE.md) for the two fallbacks that are documented to work in
a cloud session regardless: copying the skills and agents you want into the
repository's own `.claude/` directory, and putting the rules in `CLAUDE.md`.

Do not read this page as a promise that installing the toolkit once makes it "on
everywhere". It does not. See the next section.

## What is not true, however convenient it would be

- **There is no global, automatic, always-on installation.** Plugins are installed
  per scope — user, project or local — and a project-scoped declaration still needs
  each person to trust the folder, and may still need a one-time install.
- **Claude Code has no cross-session memory here.** `docs/ai/PROJECT_STATE.md` is a
  tracked file that gets read again because it is committed. Nothing is remembered.
- **Hooks are not a security boundary.** They see only what Claude Code routes
  through them, they can be disabled, and they are inert without Python 3 exposed as `python`.
- **A committed settings file cannot grant permissions silently.** `allow` rules and
  `additionalDirectories` wait for the workspace-trust dialog; `deny` and `ask` rules
  apply immediately. This toolkit ships deny rules only, so nothing waits and nothing
  is granted.
- **`~/.claude` is not available in a cloud session** in the way it is locally.
  Everything this toolkit needs is therefore committed to a repository.

## Requirements

| Requirement | Why | If absent |
| --- | --- | --- |
| Claude Code new enough for `/plugin` and marketplaces | Everything | Update Claude Code; `claude --version` reports what you have |
| `git` | Every git-state check | The workflow does not apply |
| Python 3 as `python` on `PATH` | The four hook scripts, and the validation suite | Hooks fail, which Claude Code treats as non-blocking, so they are simply inert. Skills are unaffected |

No other runtime dependency. The toolkit adds nothing to your project's dependency
tree — see check 26.

## Deliberate exclusions in 0.1.0

- **No MCP servers.** No `.mcp.json`, no `mcpServers` key. An MCP server runs with
  meaningful access, and adding one would be a trust decision this version does not
  make for you. Check 27 enforces the absence.
- **No third-party plugin dependencies.** No `dependencies` array in any manifest.
- **No Claude-Mem and no OmniRoute.** Excluded by requirement; checks 18 and 19 fail
  the build if a reference appears.
- **No `allowed-tools` on any skill, and no `permissions.allow` rule anywhere.**

## How to re-verify this page

```bash
claude --version
claude plugin validate .
python tests/run_validation.py
python tests/run_hook_commands.py
```

Then re-read the documentation URLs in the table above. If a format has changed,
update the manifests and this page in the same commit, and record the date and CLI
version at the top. A compatibility page with a stale date is worse than none.
