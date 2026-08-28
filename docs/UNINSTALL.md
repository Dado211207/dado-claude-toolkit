# Uninstall

Removing this toolkit leaves nothing behind in your repositories. No plugin here
writes a file into a project — everything a project gets, you copied there yourself.

## Turn it off without removing it

Fastest, and reversible:

```bash
claude plugin disable dado-core@dado-tools
claude plugin disable dado-web-quality@dado-tools
claude plugin disable dado-ui-design@dado-tools
claude plugin disable dado-python-windows@dado-tools
claude plugin disable dado-content-localization@dado-tools
claude plugin disable dado-release-safety@dado-tools
```

Re-enable with `claude plugin enable <plugin>@dado-tools`.

To silence the hooks only, set `"disableAllHooks": true` in your settings — note that
this disables **every** hook from every source, not only this toolkit's.

## Uninstall the plugins

```bash
claude plugin uninstall dado-core@dado-tools
claude plugin uninstall dado-web-quality@dado-tools
claude plugin uninstall dado-ui-design@dado-tools
claude plugin uninstall dado-python-windows@dado-tools
claude plugin uninstall dado-content-localization@dado-tools
claude plugin uninstall dado-release-safety@dado-tools
```

Add `--scope project` or `--scope local` to target a specific scope.

If a plugin was enabled by a project's shared `.claude/settings.json`, Claude Code
asks which you mean: disable it for yourself (an override in your
`.claude/settings.local.json`, leaving it installed for the project) or uninstall it
for everyone (removing it from the shared file).

## Remove the marketplace

```bash
claude plugin marketplace remove dado-tools
```

Removing a marketplace uninstalls the plugins you installed from it. Do this last.

## Clean up your repository

The toolkit created none of these — you did, by following a profile. Remove what you
no longer want:

| File | What to do |
| --- | --- |
| `.claude/settings.json` | Delete the `extraKnownMarketplaces` and `enabledPlugins` blocks. **Keep the `permissions.deny` rules** if they are useful — they work with or without the toolkit |
| `CLAUDE.md` | Remove the appended profile snippet |
| `.claude/dado-web-quality.json` | Delete if you no longer want it |
| `.claude/dado-protected-terms.json` | Consider keeping — it is your record of approved terms |
| `docs/ai/PROJECT_STATE.md` | Yours. Keep or delete |
| `docs/ai/CONTENT-FACTS.md` | Consider keeping — it is your record of approved facts |
| `docs/release/VERIFICATION-LEVELS.md` | Consider keeping — it is useful on its own |
| `docs/release/MANUAL-ACCEPTANCE-CHECKLIST.md` | Consider keeping |

Removing the settings blocks does not affect anyone who installed the plugins to
their own user scope; they uninstall separately.

## Confirm it is gone

```bash
claude plugin list
claude plugin marketplace list
```

Neither should mention `dado-tools`. In a session, `/plugin` → **Installed** should
show nothing from this marketplace, and `/help` → **Custom commands** should show no
`dado-*` skills.

If plugin skills still appear after uninstalling, clear the cache and restart:

```bash
rm -rf ~/.claude/plugins/cache
```

## What is not removed, and why

- **Anything you copied into your own repositories.** Those files are yours. The list
  above says which are worth keeping.
- **Permission deny rules.** They restrict rather than grant, they are independent of
  the toolkit, and deleting them makes your setup less safe, not cleaner.
- **Habits.** The honesty rules are just rules. They work without any plugin
  installed.
