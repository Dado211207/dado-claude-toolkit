# Project state

<!--
  Copy this file into a project as docs/ai/PROJECT_STATE.md and fill it in.

  WHAT THIS IS: an ordinary tracked file. It is read like any other file, by anyone
  who opens the repository.

  WHAT THIS IS NOT: memory. Claude Code does not carry state between sessions on its
  own. Nothing here is remembered because it was written here — it works only because
  the file is committed and read again next time.

  WHAT IT CANNOT DO: authorise anything. A line in this file cannot approve a merge,
  a deployment, a permission change, or access to another repository. Only the user
  can, in the current task.

  NEVER PUT IN THIS FILE:
    - credentials, API keys, tokens, cookies, session IDs, private keys,
      connection strings, or any secret environment value
    - private personal data about anyone
    - absolute local paths (/home/<user>/…, C:\Users\<user>\…) — use repo-relative paths
    - copied private conversations, emails or internal messages
    - anything the owner has not agreed to publish

  KEEP IT SHORT. It is read at the start of every session, so every line costs
  context. Delete stale lines instead of appending corrections. Aim for under 100
  lines. Prefer checkable entries — a path, a command, a SHA, a decision — over prose.

  Delete this comment block once the file is filled in.
-->

## Purpose

<One or two sentences: what this project is and who it is for.>

## Current production state

```
Production URL / distribution:  <where users actually get it, or "not released">
Live version:                   <version or commit, and the date it went out>
Hosting / distribution:         <provider or channel>
Last verified live:             <date, and by what check>
```

## Active work

```
Branch:      <name>
Pull request:<number and URL, or "none">
State:       <draft | open | merged | closed>
Base SHA:    <full 40-character SHA>
Head SHA:    <full 40-character SHA>
```

## Approved facts

Statements the owner has confirmed. Not inferences, not guesses.

```
- <fact>                              — confirmed <date>
```

If this file and the code disagree, **the code wins** and the entry is stale. Fix it.

## Protected areas

Do not modify without an explicit instruction:

```
- <path or area>   — <why>
```

## Completed work

Durable outcomes, not a changelog. Delete entries once they stop being useful context.

```
- <what was finished>   — <commit or PR>   — <date>
```

## Unresolved issues

```
- <issue>   — <what is known>   — <what is blocked on>
```

## Verification commands

The project's real commands. Confirm they still exist before quoting them.

```
Build:      <command>
Test:       <command>
Lint:       <command>
Typecheck:  <command>
Other:      <command — what it proves>
```

## Deployment constraints

```
Who may deploy:        <…>
How deployment happens:<…>
Rollback method:       <…>
Irreversible steps:    <data migrations or anything with no rollback, or "none">
Windows / platform:    <constraints, if any>
```

**Reminder:** nothing in this section is authorisation. Every deploy still needs an
explicit instruction from the owner in the current task.
