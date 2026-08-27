#!/usr/bin/env python3
"""dado-release-safety PreToolUse guard: ask before irreversible or outward-facing commands.

Contract with Claude Code (see https://code.claude.com/docs/en/hooks):

  * stdin  : one JSON object describing the pending Bash or PowerShell call
  * stdout : nothing, or a JSON object with hookSpecificOutput
  * exit 0 : always, unless Python itself fails

This hook only ever emits ``escalate`` — it forces the user's own permission prompt
to appear for a matched command. It never emits ``allow`` (which would suppress that
prompt) and never emits ``deny`` (blocking a command the user may legitimately want
is not this hook's job; making the decision visible is).

Limits, stated plainly: this is a speed bump, not a security boundary. It matches
text, so an equivalent command written differently, built at runtime, or run from a
script file will not match. It is inert without ``python`` on PATH. Do not rely on
it to contain an untrusted agent.

Side effects: none. Reads stdin, writes stdout, touches no file and no network.
"""

from __future__ import annotations

import json
import re
import sys

# (compiled pattern, why it matters). Order matters only for which reason is shown.
RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bgit\s+push\b[^\n]*(--force\b|--force-with-lease\b|(?<!\w)-f(?!\w))"),
     "force-pushing rewrites remote history and can destroy someone else's commits"),
    (re.compile(r"\bgit\s+push\b[^\n]*--delete\b"),
     "this deletes a remote branch or tag"),
    (re.compile(r"\bgit\s+push\b[^\n]*\s:\S"),
     "the refspec ':name' deletes a remote ref"),
    (re.compile(r"\bgit\s+push\b[^\n]*--tags\b"),
     "pushing tags publishes a release marker"),
    (re.compile(r"\bgit\s+reset\s+[^\n]*--hard\b"),
     "a hard reset discards uncommitted work irreversibly"),
    (re.compile(r"\bgit\s+clean\b[^\n]*-[a-zA-Z]*[fx]"),
     "git clean deletes untracked files, including files the user has not committed"),
    (re.compile(r"\bgit\s+branch\s+[^\n]*-D\b"),
     "-D force-deletes a branch even if it is unmerged"),
    (re.compile(r"\bgit\s+tag\s+[^\n]*-d\b"),
     "this deletes a tag"),
    (re.compile(r"\bgit\s+(filter-branch|filter-repo)\b"),
     "this rewrites the whole history of the repository"),
    (re.compile(r"\bgit\s+update-ref\s+[^\n]*-d\b"),
     "this deletes a git ref directly"),
    (re.compile(r"\bgit\s+reflog\s+expire\b"),
     "expiring the reflog removes the last safety net for recovering lost commits"),
    (re.compile(r"\bgit\s+stash\s+(drop|clear)\b"),
     "this discards stashed user work"),
    (re.compile(r"\bgit\s+commit\b[^\n]*--amend\b"),
     "amending rewrites the previous commit"),
    (re.compile(r"\bgit\s+merge\b"),
     "merging is a stop-line action that needs a task-specific instruction"),
    (re.compile(r"\bgit\s+(checkout|restore)\s+[^\n]*--\s"),
     "this overwrites working-tree files from the index or a commit"),
    (re.compile(r"\bgh\s+pr\s+merge\b"),
     "merging a pull request needs a task-specific instruction"),
    (re.compile(r"\bgh\s+(release|repo)\s+(create|delete|edit)\b"),
     "this changes a release or the repository itself"),
    (re.compile(r"\bgh\s+api\b[^\n]*-X\s*(DELETE|PATCH|PUT|POST)\b"),
     "this is a write call against the GitHub API"),
    (re.compile(r"\bnpm\s+publish\b|\byarn\s+publish\b|\bpnpm\s+publish\b"),
     "publishing a package is irreversible for that version"),
    (re.compile(r"\b(netlify|vercel)\b[^\n]*(--prod\b|\bdeploy\b)"),
     "this deploys to a hosting provider"),
    (re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r"),
     "recursive force delete is irreversible"),
    (re.compile(
        r"\bRemove-Item\b[^\n]*(?:-(?:Recurse|r)\b[^\n]*-(?:Force|fo)\b|"
        r"-(?:Force|fo)\b[^\n]*-(?:Recurse|r)\b)",
        re.IGNORECASE,
     ),
     "PowerShell recursive force delete is irreversible"),
)


def find_reason(command: str) -> str | None:
    for pattern, reason in RULES:
        if pattern.search(command):
            return reason
    return None


def main() -> int:
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        return 0
    if not isinstance(payload, dict):
        return 0

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return 0

    reason = find_reason(command)
    if reason is None:
        return 0

    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "escalate",
                    "permissionDecisionReason": (
                        "dado-release-safety: confirm this yourself — "
                        f"{reason}. Approve only if you asked for exactly this "
                        "in the current task."
                    ),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open: a broken guard must never block ordinary work.
        sys.exit(0)
