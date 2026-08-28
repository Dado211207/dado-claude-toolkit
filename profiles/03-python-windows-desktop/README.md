# Profile 03 — Python desktop application for Windows

For a Python desktop app packaged with PyInstaller and distributed with an Inno Setup
installer. Nothing in this profile or in `dado-python-windows` is specific to any
particular application: fill in your own paths, names and commands.

## Plugins

| Plugin | Why |
| --- | --- |
| `dado-core` | Orientation, safe editing, test selection, honest reporting |
| `dado-ui-design` | Desktop information architecture, visual hierarchy, accessibility, interaction and WPF/WinUI implementation guidance |
| `dado-python-windows` | Windows code review, packaging, installer lifecycle, devices, Windows CI |
| `dado-release-safety` | The stop line before a build is published to users |

## Install

```bash
claude plugin marketplace add Dado211207/dado-claude-toolkit
claude plugin install dado-core@dado-tools
claude plugin install dado-ui-design@dado-tools
claude plugin install dado-python-windows@dado-tools
claude plugin install dado-release-safety@dado-tools
```

## Files to copy

| From | To |
| --- | --- |
| `settings.json` | `.claude/settings.json` (merge by hand if one exists) |
| `CLAUDE.md.snippet.md` | append to `CLAUDE.md` |
| `plugins/dado-python-windows/templates/VERIFICATION-LEVELS.md` | `docs/release/VERIFICATION-LEVELS.md` |
| `plugins/dado-python-windows/templates/MANUAL-ACCEPTANCE-CHECKLIST.md` | `docs/release/MANUAL-ACCEPTANCE-CHECKLIST.md` |

## Required tools

| Tool | Needed for | If missing |
| --- | --- | --- |
| Python 3 + the project's package manager | Everything | Nothing runs |
| PyInstaller | Building the executable | Packaging checks are `not-run` |
| Inno Setup (`ISCC.exe`) | Compiling the installer | Installer checks are `not-run` |
| A Windows machine or runner | L3–L5 verification | Only static review is possible; label it as inference |
| `sha256sum` / `Get-FileHash` | Artifact digests | Artifact identity is unverifiable |
| A real PC with audio, microphone and a display | L6 manual acceptance | Cannot be substituted by anything |

## Verification levels

Copy the table from `docs/release/VERIFICATION-LEVELS.md` into each release record
and fill it in. The point of the table is that levels never substitute for each
other:

| Level | Proves | Does not prove |
| --- | --- | --- |
| L1 unit | Logic in isolation | Integration, packaging, Windows |
| L2 integration | Modules together | The packaged artifact |
| L3 packaged product | Hidden imports, data files, start/quit | Installer, upgrade, devices |
| L4 Windows CI | L1–L3 reproducibly, portability, orphan detection | Audio, mic, GPU, antivirus, SmartScreen, installer UI |
| L5 installed product | Install, upgrade, uninstall, purge, migration | Real-device behaviour, real-user experience |
| L6 real-PC manual | Sound, microphone, speech, scaling, how it feels | Only what the human actually did |

## Suggested verification commands

```bash
# L1 / L2 — any OS
python -m pytest -q

# L3 — build and inspect (Windows)
pyinstaller <name>.spec --noconfirm --clean
Get-ChildItem -Recurse dist\<name> | Select-Object FullName, Length
Get-Content build\<name>\warn-<name>.txt

# L3 — start and quit five times, then check for orphans
#   see /dado-python-windows:windows-ci-portability for the loop

# Installer (Windows)
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\<name>.iss
Get-FileHash -Algorithm SHA256 dist\<name>-setup.exe
Get-AuthenticodeSignature dist\<name>-setup.exe | Format-List Status, StatusMessage
```

## What remains manual

- Installing the plugins and confirming the trust prompt.
- **L5 and L6 in full.** Clean install, upgrade over the previous release with real
  data, uninstall preserving data, full purge, migration — and everything involving
  a microphone, a speaker, a camera, a GPU, an antivirus product, a SmartScreen
  reputation check, an elevation prompt, or a human's judgement.
- Code signing. `signtool` is denied in the settings above on purpose.
- Publishing a release. `gh release` is denied on purpose.

An agent must never tick an item in the manual acceptance checklist. The correct
agent output is that checklist with every item left `not-tested`, handed to you.

## Reporting rules that matter most here

- Report signature status exactly as observed: `signed — valid, issuer <name>` /
  `signed — invalid (<reason>)` / `unsigned` / `not checked`.
- Disclose SmartScreen: an unsigned installer, or a newly signed one without
  reputation, shows the "unrecognised app" warning. Report `not observed` unless it
  was actually downloaded and run on a real Windows machine.
- Never write that an artifact is "safe", "trusted" or "will not be flagged".
- Static review of Windows behaviour from a Linux session is inference. Label it.

## Remove it cleanly

```bash
claude plugin uninstall dado-release-safety@dado-tools
claude plugin uninstall dado-python-windows@dado-tools
claude plugin uninstall dado-ui-design@dado-tools
claude plugin uninstall dado-core@dado-tools
claude plugin marketplace remove dado-tools     # optional
```

Then remove the `extraKnownMarketplaces` and `enabledPlugins` blocks from
`.claude/settings.json` and the snippet from `CLAUDE.md`. The templates you copied
into `docs/release/` are yours — keep them; they are useful without the plugin.
