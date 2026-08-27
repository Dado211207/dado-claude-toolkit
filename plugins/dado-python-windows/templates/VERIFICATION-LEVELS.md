# Verification levels for a Windows desktop application

Copy this table into a project's release checklist. Its purpose is to stop a green
tick at one level from being reported as coverage at another.

Fill in the right-hand columns per release. A level that was not performed is
`not-run`, never blank and never assumed.

| Level | Runs where | Proves | Does **not** prove | This release |
| --- | --- | --- | --- | --- |
| **L1 — Unit** | Any OS, seconds | Pure logic, parsing, formatting, state transitions in isolation | Anything about integration, packaging, or Windows | `pass / fail / not-run` |
| **L2 — Integration** | Any OS, minutes | Modules working together, real files, real subprocesses, local services | Windows-specific behaviour, the packaged artifact | `pass / fail / not-run` |
| **L3 — Packaged product** | Windows, from the built `.exe` | Hidden imports resolved, data files present, resource paths correct, app starts and quits, no orphan process | Installer behaviour, upgrade path, devices | `pass / fail / not-run` |
| **L4 — Windows runner (CI)** | Windows CI VM | L1–L3 reproducibly, plus path/encoding portability, repeated start-quit cycles, installer compiles | Audio, microphone, camera, GPU, antivirus, SmartScreen, installer UI, permission dialogs | `pass / fail / not-run` |
| **L5 — Installed product** | A real or virtual Windows machine, installed from the installer | Clean install, upgrade over the previous release, uninstall preserving data, full purge, migration, elevation behaviour | Real-device behaviour, real-user experience | `pass / fail / not-run` |
| **L6 — Real-PC manual acceptance** | A human on real hardware | Sound audible, microphone captures, speech usable, tray discoverable, visual correctness, display scaling, antivirus and SmartScreen reaction as a real user sees it | Nothing beyond what the human actually did | `pass / fail / not-run` |

## Rules

1. **A level is only "pass" if it was performed for this build.** Record the artifact
   SHA-256 each level was run against. A pass against a different build is not a pass.

2. **Levels do not substitute for each other.** L4 green does not imply L5. L5 green
   does not imply L6. Say which levels ran.

3. **L6 cannot be performed by an agent.** Anything requiring a microphone, a
   speaker, a camera, a GPU, a real antivirus install, a real SmartScreen reputation
   check, or a human's judgement is `requires-manual-acceptance` and belongs to the
   user. An agent may prepare the checklist; it may not tick it.

4. **Record the environment for every level**: OS version, account type (standard or
   administrator), machine kind (real PC, VM, CI runner), and whether it was a clean
   machine or one with a previous version installed.

## Release record

```
Version:        <…>
Commit:         <full SHA>
Installer:      <file> sha256=<digest>
Signature:      signed (valid|invalid: <reason>) | unsigned | not checked

L1 unit:              <result>  — <command> -> exit <code> (<counts>)
L2 integration:       <result>  — <command> -> exit <code> (<counts>)
L3 packaged product:  <result>  — <where>
L4 windows runner:    <result>  — <workflow run URL>
L5 installed product: <result>  — <machine, scenarios run>
L6 manual acceptance: <result>  — <who, when, which checklist items>

Not run:        <levels and why>
Known gaps:     <what nobody verified for this release>
```
