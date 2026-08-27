# Real-PC manual acceptance checklist (L6)

For a human, on real Windows hardware. An agent may prepare this file; it must not
fill in the results.

```
Tester:          <name>
Date:            <date>
Machine:         <real PC | VM>  — Windows <version>  — <standard | administrator>
Previous state:  <clean machine | version <…> already installed>
Installer:       <file>  sha256=<digest>
```

Mark each item `pass`, `fail`, `n/a` or `not-tested`. Add a note for anything that is
not a clean pass.

## Install

- [ ] Download completes; the browser does not block the file
- [ ] SmartScreen: **record exactly what appeared** — no warning / "unrecognised app"
      / blocked. Note whether "More info → Run anyway" was needed
- [ ] Antivirus: no detection, or record the product and the exact detection name
- [ ] Installer UI is readable, correctly worded, and shows the right version
- [ ] Elevation is requested only if a per-machine install requires it
- [ ] Install completes without an error dialog

## First run

- [ ] The app launches from the Start Menu shortcut
- [ ] The app launches from the desktop shortcut (if one was created)
- [ ] The main window appears within a reasonable time — record how long
- [ ] The tray icon appears, has the right tooltip, and its menu opens
- [ ] Text is legible at 100% display scaling
- [ ] Text is legible and the layout is intact at 125%, 150% and 200% scaling
- [ ] The window behaves correctly when moved to a second monitor with a different
      scale factor

## Devices (nothing here can be automated)

- [ ] Sound plays through the default output device, audible and undistorted
- [ ] Changing the default output device while the app runs is handled
- [ ] Unplugging a headset while the app runs does not crash or hang it
- [ ] The microphone permission prompt appears the first time it is needed
- [ ] Denying microphone access produces a clear message naming Windows Settings
- [ ] After granting access in Windows Settings, the app recovers without a reinstall
- [ ] Speech-to-text transcribes normally spoken input acceptably — record an example
      of what was said and what was transcribed
- [ ] Text-to-speech output is intelligible at a normal volume

## Everyday use

- [ ] The primary workflow completes end to end
- [ ] The UI stays responsive during the longest operation
- [ ] Errors are shown to the user rather than only written to a log
- [ ] Settings persist across a restart
- [ ] Stored credentials still work after a restart

## Shutdown

- [ ] Quitting from the tray menu closes the app
- [ ] Closing the window does what the product intends (exit, or minimise to tray)
- [ ] No process remains: check Task Manager, and any child process by name
- [ ] The tray icon disappears (no ghost icon left after hovering)
- [ ] Starting and quitting five times in a row leaves nothing behind

## Upgrade (only on a machine that had the previous version)

- [ ] Installing over the previous version upgrades in place
- [ ] Apps & Features shows **one** entry, with the new version
- [ ] Settings, saved data and stored credentials survive
- [ ] Installing while the app is running is handled: it asks, or closes it cleanly

## Uninstall and purge

- [ ] Uninstall from Apps & Features completes
- [ ] User data is **preserved** by a normal uninstall
- [ ] Reinstalling finds the preserved data
- [ ] The full purge path is opt-in, clearly described, and removes what it says
- [ ] After a purge, a fresh install behaves like a first install

## Result

```
Overall:      accept | accept with notes | reject
Failed items: <list>
Notes:        <anything the tester observed that the checklist did not ask about>
Not tested:   <items and why>
```

**Reporting rule.** Only items a human actually performed may be marked `pass`. An
agent that fills in this checklist is fabricating test results — the correct agent
output is this file with every item left `not-tested`, handed to the user.
