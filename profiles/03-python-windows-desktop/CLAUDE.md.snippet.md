<!-- Append to the project's CLAUDE.md. Edit the placeholders. -->

## Working rules

Start any non-trivial change with `/dado-core:orient`. Review Windows-specific code
with `/dado-python-windows:python-app-review` before packaging.

### Commands (the real ones for this project)

```
Install deps:  <e.g. pip install -e ".[dev]">
Run from src:  <e.g. python -m <package>>
Unit tests:    <e.g. python -m pytest -q>
Lint:          <e.g. ruff check .>
Typecheck:     <e.g. mypy <package>>
Build exe:     <e.g. pyinstaller <name>.spec --noconfirm --clean>
Build setup:   <e.g. ISCC.exe installer\<name>.iss>
```

### Windows rules for this project

- Resolve executables with `shutil.which`; treat `None` as an expected outcome with a
  clear message, never a traceback.
- Read bundled resources through the `sys._MEIPASS`-aware helper. Nothing reads a
  file "next to the script".
- Writable data goes under `%LOCALAPPDATA%` / `%APPDATA%`, never next to the
  executable — `Program Files` is not writable for a standard user.
- Subprocesses: argument **list**, `shell=False`, a `timeout`, output drained,
  explicit encoding with `errors="replace"`, `CREATE_NO_WINDOW` for background
  children. Never pass a secret as a command-line argument.
- Every spawned child has an owner that terminates it:
  `terminate()` → bounded wait → `kill()` → `wait()`.
- Worker threads are daemons **or** joined on shutdown — not neither.
- Local services bind `127.0.0.1`, never `0.0.0.0`, and require a per-session token
  for anything that mutates state.
- Credentials live in Windows Credential Manager. Never in a file, never in the
  registry in plain text, never in a log, never in an error message.
- **Never read, print, enumerate or export a stored credential** — check only whether
  an entry exists.

### Verification levels

See `docs/release/VERIFICATION-LEVELS.md`. State which levels ran for a build, and
against which artifact SHA-256. Levels never substitute for each other.

- L1–L2 can run anywhere.
- L3–L4 need Windows.
- L5 needs a real or virtual Windows machine and an installer.
- **L6 needs a human on real hardware and cannot be performed by an agent.**

### The hardware rule

Never claim that a microphone, speaker, camera, GPU, antivirus product, SmartScreen
reputation check, installer dialog, Windows permission prompt, or a real user's
experience was tested unless it actually was, on real hardware, by a human. Mark
those `requires-manual-acceptance` and hand them back.

Static review of Windows behaviour from a non-Windows session is inference. Say so.

### Reporting

- `<command> -> exit <code>  (<n> passed, <n> failed, <n> skipped)` for every check.
- Signature status exactly as observed; never "safe" or "trusted".
- SmartScreen: `not observed` unless you ran the installer on a real Windows machine.
- Artifact claims carry `sha256=<digest>` and the commit they were built from.

### Stop line

No release, tag, signing, publish or upgrade rollout without an explicit instruction
in the current task. A green Windows CI job is not authorisation.
