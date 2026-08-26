#!/usr/bin/env python3
"""dado-release-safety PreToolUse guard: ask before editing files on a protected branch.

Contract with Claude Code (see https://code.claude.com/docs/en/hooks):

  * stdin  : one JSON object describing the pending Write/Edit call
  * stdout : nothing, or a JSON object with hookSpecificOutput
  * exit 0 : always, unless Python itself fails

This hook only ever emits ``escalate``. It never emits ``allow`` (which would
suppress the user's permission prompt) and never ``deny`` (working directly on
``main`` in your own repository is legitimate; doing it *without noticing* is the
problem).

Protected branch names default to main, master, prod, production, release, stable.
Override with the ``DADO_PROTECTED_BRANCHES`` environment variable, a comma-separated
list. The value is used for comparison only and is never printed.

Limits: this is a speed bump, not branch protection. Real branch protection lives on
the git host. The hook is inert without ``python3`` or ``git`` on PATH.

Side effects: runs ``git rev-parse --abbrev-ref HEAD`` (read-only, no shell, 5s cap)
in the session's working directory. Writes no file and makes no network call.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

DEFAULT_PROTECTED = ("main", "master", "prod", "production", "release", "stable")


def protected_names() -> frozenset[str]:
    raw = os.environ.get("DADO_PROTECTED_BRANCHES", "")
    names = [n.strip().lower() for n in raw.split(",") if n.strip()]
    return frozenset(names or DEFAULT_PROTECTED)


def current_branch(cwd: str) -> str | None:
    if not cwd or not os.path.isdir(cwd):
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    # "HEAD" means a detached checkout; there is no branch to protect.
    return branch or None


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

    cwd = payload.get("cwd")
    if not isinstance(cwd, str):
        return 0

    branch = current_branch(cwd)
    if branch is None or branch == "HEAD":
        return 0
    if branch.lower() not in protected_names():
        return 0

    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path") or "a file"
    if not isinstance(target, str):
        target = "a file"

    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "escalate",
                    "permissionDecisionReason": (
                        f"dado-release-safety: the checkout is on '{branch}', a protected "
                        f"branch, and this would edit {target}. Work on a feature branch "
                        "unless you asked for a direct change to this branch."
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
