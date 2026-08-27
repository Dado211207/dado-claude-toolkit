#!/usr/bin/env python3
"""dado-core PreToolUse guard: refuse writes that target obvious secret material.

Contract with Claude Code (see https://code.claude.com/docs/en/hooks):

  * stdin  : one JSON object describing the pending tool call
  * stdout : either nothing, or a JSON object with hookSpecificOutput
  * exit 0 : always, unless Python itself fails

This hook only ever emits ``deny`` or ``escalate``. It never emits ``allow``:
emitting ``allow`` would suppress the user's normal permission prompt, which would
turn a safety hook into a permission grant. When nothing matches, it prints nothing
and exits 0, so the normal permission flow applies unchanged.

Limits, stated plainly: this is a convenience guard, not a security boundary. It
sees only the tool calls Claude Code routes through it, it can be disabled by the
user at any time, and it does nothing at all if ``python`` is not on PATH. Do not
rely on it to contain an untrusted agent.

Side effects: none. It reads stdin, writes stdout, and touches no file, no network
and no environment variable.
"""

from __future__ import annotations

import json
import os
import re
import sys

# --- what counts as secret material -----------------------------------------

# Exact file names that hold credentials. Writing to any of these is refused.
DENY_BASENAMES = frozenset(
    {
        ".git-credentials",
        ".htpasswd",
        "credentials",
        "credentials.json",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "id_rsa",
        "secrets.json",
        "secrets.yaml",
        "secrets.yml",
    }
)

# Extensions that are private key or keystore material.
DENY_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".ppk")

# Directories that belong to a credential store, anywhere in the path.
DENY_PATH_PARTS = (".ssh", ".gnupg", ".aws", ".azure", ".kube")

# Names that usually hold a token but are also edited legitimately: ask, do not block.
ASK_BASENAMES = frozenset({".npmrc", ".pypirc", ".netrc", "_netrc"})

# `.env` variants that are documented placeholders and therefore fine to write.
ENV_ALLOWED_SUFFIXES = ("example", "sample", "template", "defaults", "schema", "dist")

# Pattern parts are concatenated on purpose: the joined literal must not appear in
# this file, or every secret scanner (including this toolkit's own) flags the
# scanner as a finding.
_PEM_PRIVATE = re.compile(r"-----BEGIN [A-Z ]*PRI" + r"VATE KEY-----")

_TOKEN_SHAPES = (
    re.compile(r"\bAKIA" + r"[0-9A-Z]{16}\b"),          # AWS access key id
    re.compile(r"\bgh[pousr]_" + r"[A-Za-z0-9]{36,}"),  # GitHub token
    re.compile(r"\bsk-ant-" + r"[A-Za-z0-9_\-]{24,}"),  # Anthropic API key
    re.compile(r"\bxox[baprs]-" + r"[A-Za-z0-9-]{10,}"),  # Slack token
    re.compile(r"\bAIza" + r"[0-9A-Za-z_\-]{35}\b"),    # Google API key
)


def decide_path(file_path: str) -> tuple[str, str] | None:
    """Return (decision, reason) for a write target, or None to stay silent."""
    if not file_path:
        return None

    normalised = file_path.replace("\\", "/")
    base = os.path.basename(normalised)
    lower = base.lower()
    parts = {p.lower() for p in normalised.split("/") if p}

    hit = parts & set(DENY_PATH_PARTS)
    if hit:
        return ("deny", f"path is inside a credential store directory ({sorted(hit)[0]})")

    if lower in DENY_BASENAMES:
        return ("deny", f"{base} holds credentials")

    if lower.endswith(DENY_SUFFIXES):
        return ("deny", f"{base} looks like private key or keystore material")

    if lower == ".env" or lower.startswith(".env."):
        tail = lower[len(".env.") :] if lower.startswith(".env.") else ""
        if not any(tail.startswith(ok) or tail.endswith(ok) for ok in ENV_ALLOWED_SUFFIXES):
            return ("deny", f"{base} holds environment secrets")

    if lower.endswith(".env") and lower != ".env":
        return ("deny", f"{base} holds environment secrets")

    if lower in ASK_BASENAMES:
        return ("escalate", f"{base} commonly holds an auth token")

    return None


def decide_content(text: str) -> tuple[str, str] | None:
    """Return (decision, reason) for written content, or None to stay silent."""
    if not text:
        return None
    if _PEM_PRIVATE.search(text):
        return ("deny", "the content contains a PEM private key block")
    for shape in _TOKEN_SHAPES:
        if shape.search(text):
            return ("escalate", "the content matches the shape of a provider API token")
    return None


def extract(payload: dict) -> tuple[str, str]:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return "", ""
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    chunks = [
        tool_input.get("content"),
        tool_input.get("new_string"),
        tool_input.get("new_source"),
    ]
    text = "\n".join(c for c in chunks if isinstance(c, str))
    return (path if isinstance(path, str) else ""), text


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

    path, text = extract(payload)
    verdict = decide_path(path) or decide_content(text)
    if verdict is None:
        return 0

    decision, reason = verdict
    target = path or "the written content"
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": (
                        f"dado-core secret guard: refusing to write {target} because "
                        f"{reason}. Secrets must never enter tracked files. If this "
                        f"file is genuinely a placeholder, rename it to a documented "
                        f"*.example form, or disable this hook (see the dado-core README)."
                        if decision == "deny"
                        else f"dado-core secret guard: {target} — {reason}. "
                        f"Confirm this write yourself before it runs."
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
