# Maintenance

## Updating a marketplace safely

Third-party marketplaces have auto-update **off** by default. Keep it off, and update
deliberately:

```bash
cd <a clone of the toolkit>
git fetch origin
git log --oneline HEAD..origin/main          # what changed
git diff HEAD..origin/main -- plugins/*/hooks/   # the only code that executes
```

Read the hook diff first. Then:

```bash
claude plugin marketplace update dado-tools
```

Record which version you are on. Pin to a commit SHA in `extraKnownMarketplaces` if
you need content that cannot change under you — see the profile 05 README.

## Re-verifying compatibility

Claude Code changes quickly. `docs/CLAUDE-CODE-COMPATIBILITY.md` records the date and
CLI version it was researched against. Before trusting it:

```bash
claude --version
claude plugin validate .
python tests/run_validation.py
```

Then re-read the documentation URLs listed at the top of that page. If a format
changed, fix the manifests and the page in the same commit and update the date and
version. A compatibility page with a stale date is worse than none.

## Changing the toolkit

```bash
python tests/run_validation.py          # 30 checks; run before and after
python tests/run_validation.py --quick  # structural only, no subprocesses
python tests/run_validation.py --json   # machine-readable
python tests/run_hook_commands.py       # actual configured hook commands
claude plugin validate .
```

Every check exists because something can silently go wrong. If a check blocks a
change you believe is correct, change the check **in the same commit** and say why in
the message — do not weaken it quietly and do not skip it.

Adding a skill: create `plugins/<plugin>/skills/<name>/SKILL.md` with `name` and
`description` front-matter, add a row to that plugin's README (check 28 enforces the
row), and run the suite.

Adding an agent: create `plugins/<plugin>/agents/<name>.md` with `name` and
`description`, a restricted `tools` list that does **not** include `Agent`, and a
README row.

Do not add: an `allowed-tools` grant, a `permissions.allow` rule, an MCP server, a
dependency, or a hook that emits `allow`. Checks 14, 15, 16, 24, 26, 27 and 29 fail
the build on each.

## Versioning

Semantic versions. The marketplace `version`, each marketplace entry's `version` and
each `plugin.json` `version` must agree — check 6 enforces it.

Bump a plugin's patch version for a wording fix, minor for a new skill or agent,
major for a removal or a change in what a skill will do. Users only receive an update
when the version changes.

Record every change in `CHANGELOG.md`.

## Future work

Deliberately deferred from 0.1.0 to keep the first version small and reviewable.
Nothing here is missing functionality that the toolkit claims to have.

**Skills**

- `dado-core`: a dependency-change review skill; a commit-message and diff-hygiene skill
- `dado-web-quality`: a Lighthouse-run skill (0.1.0 covers interpretation only); a
  form-and-validation review; an image and font performance pass
- `dado-python-windows`: a logging and crash-report review; an auto-update mechanism review
- `dado-content-localization`: a third-language extension of `bilingual-sync`; a
  glossary-consistency skill
- `dado-release-safety`: a changelog and release-notes verification skill; a
  post-incident rollback record

**Infrastructure**

- Verify the cloud `enabledPlugins` path end to end and record the result in
  `CLOUD-USAGE.md`, replacing the current documented-but-unverified note while
  keeping the vendoring fallback until that passes
- A vendoring helper that copies selected skills into a target repository's
  `.claude/` (currently a documented manual `cp`)
- A published tag so `ref` pinning has something to point at

**Considered and rejected for now**

- MCP servers — a trust decision this version does not make for users
- Any third-party dependency — the toolkit's value is being auditable
- A hook that verifies a claimed test command produced a recorded exit result. It
  cannot be done reliably: a hook sees one tool call, not the report written later.
  The honesty rules and the report format cover it instead, imperfectly and honestly.
