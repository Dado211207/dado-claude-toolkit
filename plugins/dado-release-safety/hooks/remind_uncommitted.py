#!/usr/bin/env python3
"""dado-release-safety Stop hook: report uncommitted changes when a turn ends.

Contract with Claude Code (see https://code.claude.com/docs/en/hooks):

  * stdin  : one JSON object describing the Stop event
  * stdout : nothing, or a JSON object with a ``systemMessage``
  * exit 0 : always

This hook is advisory only. It never returns a ``decision``, so it cannot stop or
continue a turn — it only surfaces the working-tree state so a report cannot quietly
claim a clean tree that does not exist.

Side effects: runs ``git status --porcelain=v1`` and ``git rev-parse`` (read-only,
no shell, 5s cap) in the session's working directory. Writes no file, makes no
network call, and prints no environment variable.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

MAX_LISTED = 10


def git(cwd: str, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
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
    return result.stdout


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
    if not isinstance(cwd, str) or not os.path.isdir(cwd):
        return 0

    status = git(cwd, "status", "--porcelain=v1")
    if status is None:
        return 0

    entries = [line for line in status.splitlines() if line.strip()]
    if not entries:
        return 0

    branch = (git(cwd, "rev-parse", "--abbrev-ref", "HEAD") or "").strip() or "unknown"
    head = (git(cwd, "rev-parse", "HEAD") or "").strip()[:12] or "unknown"

    shown = entries[:MAX_LISTED]
    more = len(entries) - len(shown)
    listing = "\n".join(f"  {line}" for line in shown)
    if more > 0:
        listing += f"\n  … and {more} more"

    message = (
        f"dado-release-safety: the working tree is not clean "
        f"({len(entries)} entries) on branch '{branch}' at {head}.\n"
        f"{listing}\n"
        "Before reporting this task done, confirm every one of these is intended. "
        "Do not describe the tree as clean, and do not revert files you were not "
        "asked to touch."
    )

    sys.stdout.write(json.dumps({"systemMessage": message}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open: an advisory hook must never break a session.
        sys.exit(0)
