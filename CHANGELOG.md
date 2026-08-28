# Changelog

All notable changes to this repository. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions are semantic.

## [Unreleased]

### Added

- `dado-ui-design` 0.1.0 with the `/dado-ui-design:ui-ux-pro-max` skill for local,
  searchable UI/UX design guidance across web, mobile and desktop interfaces.
- A reviewed runtime snapshot of `nextlevelbuilder/ui-ux-pro-max-skill`, pinned to
  upstream commit `8bd29e775453ebcae52b6e6514fbf134df0c5770`, with MIT license and
  provenance included. No network client, external process or runtime dependency is
  added.
- Validation check 31 pins the provenance and runtime file set, rejects network or
  subprocess access, and runs a read-only JSON design-system smoke test.

## [0.1.0] — unreleased

Initial MVP. Not tagged and not released — see the note at the bottom.

### Added

**Marketplace**

- `dado-tools` (`.claude-plugin/marketplace.json`) listing five plugins, each with a
  relative `source`, a version and an independent description at the time of the
  initial MVP.

**Plugins** (all 0.1.0)

- `dado-core` — 8 skills (orient, plan-change, debug-evidence, safe-edit,
  select-tests, verify-and-report, project-state, uncertainty-log), 5 agents
  (repository-auditor, implementation-reviewer, test-investigator, security-reviewer,
  final-verifier), 1 hook (secret-file write guard), and a shared honesty-rules
  reference.
- `dado-web-quality` — 8 skills (web-audit, responsive-review, a11y-review,
  routing-and-navigation, seo-and-metadata, headers-and-hosting, browser-testing,
  deploy-preview-check), 3 agents, and a placeholder config example.
- `dado-python-windows` — 5 skills (python-app-review, packaging-verify,
  install-lifecycle-test, runtime-and-devices, windows-ci-portability), 2 agents, and
  two release templates (six verification levels; a human-only acceptance checklist).
- `dado-content-localization` — 5 skills (factual-claims-review, bilingual-sync,
  cv-consistency, copy-quality, content-diff-review), 2 agents, and two placeholder
  templates (protected terms; approved content facts).
- `dado-release-safety` — 5 skills (pre-change-snapshot, ci-evidence,
  artifact-integrity, draft-pr, deploy-gate), 2 agents, and 3 hooks (destructive
  command escalation, protected-branch escalation, an advisory uncommitted-changes
  reminder).

**Adoption profiles** — five worked examples in `profiles/`: minimal,
React/Vite/Netlify, Python/Windows desktop, bilingual content site, and
release-sensitive. Each ships a `settings.json` with **deny rules only** and a
`CLAUDE.md` snippet.

**Validation** — `tests/run_validation.py`, 30 checks, Python standard library only,
no network. Covers manifest structure, component existence and front-matter, secret
and private-key scanning, absolute-path leakage, permission grants, deployment and
merge enablement, forbidden references, profile parsing, documentation link and
command accuracy, encoding and line-ending portability, generated-file cleanliness,
runtime hook sandboxing, and rejection of 12 committed invalid fixtures plus
generated dangerous content.

**CI** — `.github/workflows/validate.yml`: `contents: read` only, no secrets, runs
the suite twice on Linux and Windows, executes the configured hook commands, and
requires the official root and per-plugin validators from Claude Code 2.1.246.

**Documentation** — README plus INSTALL, UNINSTALL, LOCAL-USAGE, CLOUD-USAGE,
GITHUB-ACTIONS, ADOPTION, MAINTENANCE, SECURITY, THREAT-MODEL,
TRUST-AND-PERMISSIONS, CLAUDE-CODE-COMPATIBILITY and TROUBLESHOOTING, and a
`PROJECT_STATE` template.

### Deliberately not included

- No MCP servers, and no `mcpServers` key anywhere (check 27).
- No third-party runtime dependency, no lockfile, no non-stdlib import (check 26).
- No `permissions.allow` rule and no skill `allowed-tools` grant (check 14).
- No hook that emits `permissionDecision: "allow"` (checks 15 and 24).
- No agent that can spawn another agent (check 8).
- No Claude-Mem and no OmniRoute dependency (checks 18 and 19).
- No reference to any unrelated private repository (check 17).

### Known limitations

- The cloud `enabledPlugins` path is documented but **not verified end to end** by
  this repository. See `docs/CLOUD-USAGE.md`.
- The hooks are convenience guards, not a security boundary, and are inert without
  Python 3 exposed as `python` on `PATH`.
- The validation suite validates this repository, not the projects the toolkit is
  used on.
- No tag or GitHub Release exists, so `ref` pinning has no tag to point at yet; pin
  to a commit SHA instead.

Future work is listed in `docs/MAINTENANCE.md`.

---

**Release status:** 0.1.0 is on `main`, but no tag or GitHub Release has been
created. The additions under Unreleased are proposed separately and are not released.
