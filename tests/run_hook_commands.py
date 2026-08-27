#!/usr/bin/env python3
"""Execute every configured hook command exactly as the plugin declares it.

This is a cross-platform smoke test for the command boundary that the structural
suite cannot prove by importing a Python file. It intentionally reads hooks.json,
expands CLAUDE_PLUGIN_ROOT, resolves the declared interpreter from PATH, and starts
the resulting argv without a shell.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
CONFIGS = (
    REPO / "plugins/dado-core/hooks/hooks.json",
    REPO / "plugins/dado-release-safety/hooks/hooks.json",
)


def configured_commands(config: Path):
    data = json.loads(config.read_text(encoding="utf-8"))
    plugin_root = config.parent.parent
    for event, groups in data["hooks"].items():
        for group in groups:
            matcher = group.get("matcher", "")
            for handler in group.get("hooks", []):
                command = handler["command"].replace(
                    "${CLAUDE_PLUGIN_ROOT}", plugin_root.resolve().as_posix()
                )
                yield event, matcher, command


def payload_for(script_name: str, cwd: Path) -> dict:
    common = {"cwd": str(cwd), "session_id": "configured-command-smoke"}
    if script_name == "guard_secret_files.py":
        return {
            **common,
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": ".env", "content": "TOKEN=placeholder"},
        }
    if script_name == "guard_destructive_commands.py":
        return {
            **common,
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {
                "command": "Remove-Item -LiteralPath build -Recurse -Force"
            },
        }
    if script_name == "guard_protected_branch.py":
        return {
            **common,
            "hook_event_name": "PreToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": "README.md", "old_string": "a", "new_string": "b"},
        }
    if script_name == "remind_uncommitted.py":
        return {**common, "hook_event_name": "Stop"}
    raise AssertionError(f"no smoke payload for {script_name}")


def decision(stdout: str) -> str | None:
    if not stdout.strip():
        return None
    data = json.loads(stdout)
    return data.get("hookSpecificOutput", {}).get("permissionDecision")


def main() -> int:
    failures: list[str] = []
    ran = 0
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    ).stdout.strip()

    for config in CONFIGS:
        for event, matcher, command in configured_commands(config):
            argv = shlex.split(command, posix=True)
            if not argv:
                failures.append(f"{config}: empty command")
                continue
            resolved = shutil.which(argv[0])
            if not resolved:
                failures.append(f"{config}: interpreter {argv[0]!r} is not on PATH")
                continue
            argv[0] = resolved
            script_name = Path(argv[-1]).name
            payload = payload_for(script_name, REPO)
            env = os.environ.copy()
            if script_name == "guard_protected_branch.py":
                env["DADO_PROTECTED_BRANCHES"] = branch
            proc = subprocess.run(
                argv,
                input=json.dumps(payload),
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            ran += 1
            if proc.returncode != 0:
                failures.append(
                    f"{script_name}: exit {proc.returncode}; stderr={proc.stderr.strip()[:200]}"
                )
                continue
            try:
                observed = decision(proc.stdout)
            except (ValueError, TypeError) as exc:
                failures.append(f"{script_name}: invalid JSON output ({exc})")
                continue
            expected = None if script_name == "remind_uncommitted.py" else (
                "deny" if script_name == "guard_secret_files.py" else "escalate"
            )
            if observed != expected:
                failures.append(
                    f"{script_name}: decision {observed!r}, expected {expected!r} "
                    f"for {event}/{matcher}"
                )

    if ran != 4:
        failures.append(f"executed {ran} configured commands, expected 4")
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print(f"Configured hook command smoke test: {ran} passed, 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
