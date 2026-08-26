# dado-python-windows

A reusable review and release workflow for Python desktop applications on Windows.

- **Version:** 0.1.0
- **Marketplace:** `dado-tools`
- **Install:** `/plugin install dado-python-windows@dado-tools`
- **Depends on:** nothing. Pairs well with `dado-core` (honesty rules) and
  `dado-release-safety` (the stop line before a release).

## What is and is not in this plugin

Everything here is **newly written generic guidance**. The plugin contains:

- no application source code
- no content copied from any private repository
- no project-specific paths, module names, ports, GUIDs, product names or secrets
- no credentials of any kind, and no instruction to read one

It describes patterns — resource resolution under PyInstaller, subprocess argument
lists, stale single-instance locks, Credential Manager usage *as a pattern* — that
apply to any Python Windows desktop application. If you adopt it in a project, the
project-specific values live in that project, never here.

## Skills

| Skill | Invoke | What it covers |
| --- | --- | --- |
| Application review | `/dado-python-windows:python-app-review` | Executable resolution, subprocess safety, process and thread lifecycle, single-instance behaviour, localhost-only services, tray behaviour |
| Packaging verification | `/dado-python-windows:packaging-verify` | PyInstaller hidden imports and data files, one-file vs one-folder, Inno Setup script review, checksums, Authenticode status, SmartScreen disclosure |
| Install lifecycle test | `/dado-python-windows:install-lifecycle-test` | Clean install, upgrade, uninstall preserving data, full purge, legacy-data migration |
| Runtime and devices | `/dado-python-windows:runtime-and-devices` | WebView2 and browser-engine discovery, audio devices, microphone permission, speech-to-text and text-to-speech, Credential Manager patterns |
| Windows CI portability | `/dado-python-windows:windows-ci-portability` | Repeated start/quit cycles, orphan-process detection, path and encoding portability, and what a runner cannot prove |

## Agents

| Agent | Tools | Responsibility |
| --- | --- | --- |
| `dado-python-windows:python-windows-reviewer` | Read, Grep, Glob, Bash | Windows-specific code defects |
| `dado-python-windows:packaging-verifier` | Read, Grep, Glob, Bash | Build and installer artifacts, checksums, signature status |

No hooks. Neither agent can spawn further agents.

## Templates

| File | Purpose |
| --- | --- |
| `templates/VERIFICATION-LEVELS.md` | The six levels — unit, integration, packaged product, Windows runner, installed product, real-PC manual acceptance — with a release record to fill in |
| `templates/MANUAL-ACCEPTANCE-CHECKLIST.md` | The human-only checklist: install, first run, devices, everyday use, shutdown, upgrade, uninstall and purge |

Copy them into a project's release documentation and fill them in per release.

## The hardware rule

This plugin will not claim that a microphone, a speaker, a camera, a GPU, an
antivirus product, a SmartScreen reputation check, an installer dialog, a Windows
permission prompt, or a real user's experience has been tested — unless it was
actually exercised on real hardware by a human.

Those items are marked `requires-manual-acceptance` and handed to the user. An agent
filling in the manual acceptance checklist is fabricating test results; the correct
agent output is that checklist with every item left `not-tested`.

Levels never substitute for each other: a green Windows CI job does not imply the
installer works, and a working installer does not imply the speech pipeline is
usable.

## Uninstall

```
/plugin uninstall dado-python-windows@dado-tools
```

The plugin creates no files in your repository. Templates you copied into a project
are yours and stay until you delete them.
