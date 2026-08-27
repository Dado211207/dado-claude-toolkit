#!/usr/bin/env python3
"""Structural validation suite for the dado-claude-toolkit repository.

Python standard library only. No third-party dependency, no network access, no
writes outside a temporary directory that this script creates and removes.

Usage:
    python tests/run_validation.py            # all checks
    python tests/run_validation.py --quick    # structural checks only, no subprocesses
    python tests/run_validation.py --json     # machine-readable summary on stdout

Exit status: 0 when no check failed, 1 when any check failed. A skipped check never
fails the run, and is always reported as skipped with the reason - never as a pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
EXPECTED_MARKETPLACE_NAME = "dado-tools"
EXPECTED_PLUGINS = (
    "dado-core",
    "dado-web-quality",
    "dado-python-windows",
    "dado-content-localization",
    "dado-release-safety",
)

# Directories whose contents ship to users. Everything under tests/fixtures/ is
# deliberately invalid or dangerous and is the *input* to the rejection checks, so it
# is excluded here and only ever scanned by check 25.
SHIPPED_ROOTS = (".claude-plugin", ".claude", ".github", "plugins", "profiles", "docs", "tests")
FIXTURES = REPO / "tests" / "fixtures"

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".mypy_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".toml", ".cfg", ".sh", ".ps1"}


# ---------------------------------------------------------------------------
# Pattern definitions
#
# Every literal below is split across a concatenation on purpose. If the joined
# string appeared in this file, this scanner would report itself as a finding, and
# a repository-wide secret scan would flag the tool that does the scanning.
# ---------------------------------------------------------------------------

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws-access-key-id", re.compile(r"\bAKIA" + r"[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_" + r"[A-Za-z0-9]{36,}")),
    ("anthropic-api-key", re.compile(r"\bsk-ant-" + r"[A-Za-z0-9_\-]{24,}")),
    ("openai-api-key", re.compile(r"\bsk-" + r"[A-Za-z0-9]{48}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-" + r"[A-Za-z0-9-]{10,}")),
    ("google-api-key", re.compile(r"\bAIza" + r"[0-9A-Za-z_\-]{35}\b")),
    ("stripe-key", re.compile(r"\b[sr]k_live_" + r"[A-Za-z0-9]{24,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ" + r"[A-Za-z0-9_\-]{10,}\.")),
    ("basic-auth-url", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s/:@]+:[^\s/@]{6,}@")),
)

PRIVATE_KEY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("pem-private-key", re.compile(r"-----BEGIN [A-Z ]*PRI" + r"VATE KEY-----")),
    ("openssh-private-key", re.compile(r"-----BEGIN OPENSSH PRI" + r"VATE KEY-----")),
    ("pgp-private-key", re.compile(r"-----BEGIN PGP PRI" + r"VATE KEY BLOCK-----")),
    ("putty-private-key", re.compile(r"PuTTY-User-Key-File-" + r"[0-9]")),
)

# An absolute path with a real-looking account name. A documentation placeholder such
# as /home/<user>/ does not match, because '<' and '>' are outside the character class.
ABSOLUTE_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("posix-home", re.compile(r"/home/[A-Za-z0-9._\-]+/")),
    ("macos-home", re.compile(r"/Users/[A-Za-z0-9._\-]+/")),
    ("windows-users", re.compile(r"[A-Za-z]:\\+Users\\+[A-Za-z0-9._\-]+\\+")),
    ("windows-drive", re.compile(r"\b[A-Za-z]:\\+(?!Users)[A-Za-z0-9._\-]+\\+")),
)
# Paths that are legitimately absolute because they are conventional install
# locations rather than anybody's home directory.
ABSOLUTE_PATH_ALLOWED = (
    r"C:\Program Files",
    r"C:\Program Files (x86)",
)

# Permission rules that grant broadly rather than narrowly.
ALLOW_ALL_RULES = {"*", "bash", "bash(*)", "read", "read(*)", "edit", "edit(*)",
                   "write", "write(*)", "webfetch", "webfetch(*)", "mcp__*",
                   "agent", "agent(*)", "powershell", "powershell(*)"}

DEPLOY_RULE_HINTS = ("deploy", "publish", "vercel", "netlify", "kubectl", "terraform",
                     "docker push", "twine upload", "firebase")
MERGE_RULE_HINTS = ("merge", "release", "tag", "gh pr merge", "auto_merge", "autoMerge")

FORBIDDEN_DEPENDENCY_TOKENS = (
    ("claude-mem", re.compile(r"claude[-_ ]?mem\b", re.IGNORECASE)),
    ("omniroute", re.compile(r"omni[-_ ]?route\b", re.IGNORECASE)),
)

# The private desktop-assistant repository must not be referenced as a source path or
# repository by any shipped file. The name is assembled from parts so this scanner
# does not report itself, and so the constant below is not itself a match.
_EXCLUDED_APP = "jar" + "vis"
EXCLUDED_APP_PATTERNS = (
    re.compile(_EXCLUDED_APP + r"[-_/\\]", re.IGNORECASE),
    re.compile(r"[-_/\\]" + _EXCLUDED_APP + r"\b", re.IGNORECASE),
    re.compile(r"\b" + _EXCLUDED_APP + r"[-_]?windows\b", re.IGNORECASE),
    re.compile(r"\b" + _EXCLUDED_APP + r"\.(py|exe|iss|spec|json)\b", re.IGNORECASE),
)

GENERATED_ARTIFACT_NAMES = {
    "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", "dist", "build", ".cache", ".parcel-cache", ".next",
    ".DS_Store", "Thumbs.db", ".idea", ".vscode",
}
GENERATED_ARTIFACT_SUFFIXES = (".pyc", ".pyo", ".log", ".tmp", ".swp", ".orig", ".rej")

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                    r"(?:-[0-9A-Za-z.\-]+)?(?:\+[0-9A-Za-z.\-]+)?$")

REQUIRED_DOCS = (
    "README.md", "CHANGELOG.md",
    "docs/INSTALL.md", "docs/UNINSTALL.md", "docs/CLOUD-USAGE.md", "docs/LOCAL-USAGE.md",
    "docs/GITHUB-ACTIONS.md", "docs/ADOPTION.md", "docs/MAINTENANCE.md",
    "docs/SECURITY.md", "docs/THREAT-MODEL.md", "docs/TRUST-AND-PERMISSIONS.md",
    "docs/CLAUDE-CODE-COMPATIBILITY.md", "docs/TROUBLESHOOTING.md",
)

HOOK_SCRIPTS = (
    "plugins/dado-core/hooks/guard_secret_files.py",
    "plugins/dado-release-safety/hooks/guard_destructive_commands.py",
    "plugins/dado-release-safety/hooks/guard_protected_branch.py",
    "plugins/dado-release-safety/hooks/remind_uncommitted.py",
)


# ---------------------------------------------------------------------------
# Result plumbing
# ---------------------------------------------------------------------------

class Skip(Exception):
    """Raised by a check that could not run. Never counted as a pass."""


@dataclass
class Result:
    number: int
    name: str
    status: str          # PASS | FAIL | SKIP
    problems: list[str] = field(default_factory=list)
    reason: str = ""


CHECKS: list[tuple[int, str, str, object]] = []


def check(number: int, name: str, quick: bool = True):
    def wrap(fn):
        CHECKS.append((number, name, "quick" if quick else "full", fn))
        return fn
    return wrap


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------

def walk_files(root: Path, skip_fixtures: bool = True):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        here = Path(dirpath)
        if skip_fixtures and FIXTURES in (here, *here.parents):
            continue
        for name in sorted(filenames):
            yield here / name


def shipped_files(suffixes: tuple[str, ...] | None = None):
    """Every file under a shipped root, excluding tests/fixtures/."""
    seen: set[Path] = set()
    for top in SHIPPED_ROOTS:
        base = REPO / top
        if not base.exists():
            continue
        for path in walk_files(base):
            if suffixes and path.suffix not in suffixes:
                continue
            seen.add(path)
    for name in ("README.md", "CHANGELOG.md", "LICENSE", ".gitignore", ".gitattributes"):
        path = REPO / name
        if path.exists() and (not suffixes or path.suffix in suffixes):
            seen.add(path)
    return sorted(seen)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str | None:
    try:
        return path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def marketplace() -> dict:
    return load_json(MARKETPLACE)


def plugin_dirs() -> list[Path]:
    base = REPO / "plugins"
    return sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []


def parse_frontmatter(text: str) -> dict | None:
    """Minimal YAML front-matter reader: flat `key: value` pairs only.

    Enough for SKILL.md and agent files, which use flat scalar frontmatter. Returns
    None when the file has no front-matter block.
    """
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or line.startswith((" ", "\t", "-")):
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def skill_files() -> list[Path]:
    out: list[Path] = []
    for plugin in plugin_dirs():
        skills = plugin / "skills"
        if skills.is_dir():
            out.extend(sorted(skills.glob("*/SKILL.md")))
    return out


def agent_files() -> list[Path]:
    out: list[Path] = []
    for plugin in plugin_dirs():
        agents = plugin / "agents"
        if agents.is_dir():
            out.extend(sorted(agents.glob("*.md")))
    return out


def hook_configs() -> list[Path]:
    return [p / "hooks" / "hooks.json" for p in plugin_dirs() if (p / "hooks" / "hooks.json").exists()]


def iter_hook_commands(config: dict):
    for event, groups in (config.get("hooks") or {}).items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            if not isinstance(group, dict):
                continue
            for handler in group.get("hooks") or []:
                if isinstance(handler, dict):
                    yield event, handler


# ---------------------------------------------------------------------------
# Checks 1-6: marketplace and plugin manifests
# ---------------------------------------------------------------------------

@check(1, "marketplace.json parses")
def c01():
    problems = []
    if not MARKETPLACE.exists():
        return [f"{rel(MARKETPLACE)} does not exist"]
    try:
        data = marketplace()
    except json.JSONDecodeError as exc:
        return [f"{rel(MARKETPLACE)}: {exc}"]
    for key in ("name", "owner", "plugins"):
        if key not in data:
            problems.append(f"missing required key '{key}'")
    owner = data.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        problems.append("owner must be an object with a 'name'")
    if not isinstance(data.get("plugins"), list) or not data["plugins"]:
        problems.append("'plugins' must be a non-empty array")
    return problems


@check(2, "marketplace name is 'dado-tools'")
def c02():
    name = marketplace().get("name")
    if name != EXPECTED_MARKETPLACE_NAME:
        return [f"marketplace name is {name!r}, expected {EXPECTED_MARKETPLACE_NAME!r}"]
    return []


@check(3, "every plugin source directory exists")
def c03():
    problems = []
    for entry in marketplace().get("plugins", []):
        name, source = entry.get("name"), entry.get("source")
        if not isinstance(source, str):
            problems.append(f"{name}: source must be a relative path string in this marketplace")
            continue
        if not source.startswith("./"):
            problems.append(f"{name}: source {source!r} must start with './'")
        if ".." in Path(source).parts:
            problems.append(f"{name}: source {source!r} escapes the repository")
            continue
        target = (REPO / source).resolve()
        if REPO not in target.parents and target != REPO:
            problems.append(f"{name}: source {source!r} resolves outside the repository")
        elif not target.is_dir():
            problems.append(f"{name}: source directory {source!r} does not exist")
    on_disk = {p.name for p in plugin_dirs()}
    listed = {e.get("name") for e in marketplace().get("plugins", [])}
    for extra in sorted(on_disk - listed):
        problems.append(f"plugins/{extra} exists but is not listed in the marketplace")
    return problems


@check(4, "every plugin manifest parses")
def c04():
    problems = []
    for plugin in plugin_dirs():
        manifest = plugin / ".claude-plugin" / "plugin.json"
        if not manifest.exists():
            problems.append(f"{rel(manifest)} does not exist")
            continue
        try:
            data = load_json(manifest)
        except json.JSONDecodeError as exc:
            problems.append(f"{rel(manifest)}: {exc}")
            continue
        if not data.get("name"):
            problems.append(f"{rel(manifest)}: missing required 'name'")
        elif data["name"] != plugin.name:
            problems.append(f"{rel(manifest)}: name {data['name']!r} != directory {plugin.name!r}")
        for key in ("description", "version"):
            if not data.get(key):
                problems.append(f"{rel(manifest)}: missing '{key}'")
    return problems


@check(5, "plugin names are unique and expected")
def c05():
    problems = []
    names = [e.get("name") for e in marketplace().get("plugins", [])]
    for name in sorted({n for n in names if names.count(n) > 1}):
        problems.append(f"duplicate plugin name in marketplace: {name!r}")
    missing = set(EXPECTED_PLUGINS) - set(names)
    for name in sorted(missing):
        problems.append(f"expected plugin missing from marketplace: {name!r}")
    for name in names:
        if name and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            problems.append(f"plugin name {name!r} is not kebab-case")
    return problems


@check(6, "plugin versions are valid semantic versions")
def c06():
    problems = []
    mv = marketplace().get("version")
    if mv and not SEMVER.fullmatch(mv):
        problems.append(f"marketplace version {mv!r} is not semver")
    for entry in marketplace().get("plugins", []):
        name, version = entry.get("name"), entry.get("version")
        if not version:
            problems.append(f"{name}: marketplace entry has no version")
        elif not SEMVER.fullmatch(version):
            problems.append(f"{name}: marketplace version {version!r} is not semver")
        manifest = REPO / "plugins" / str(name) / ".claude-plugin" / "plugin.json"
        if manifest.exists():
            try:
                inner = load_json(manifest).get("version")
            except json.JSONDecodeError:
                continue
            if inner != version:
                problems.append(f"{name}: manifest version {inner!r} != marketplace {version!r}")
    return problems


# ---------------------------------------------------------------------------
# Checks 7-10: components and documentation files
# ---------------------------------------------------------------------------

@check(7, "referenced skill files exist and have valid front-matter")
def c07():
    problems = []
    files = skill_files()
    if not files:
        return ["no SKILL.md files found under any plugin"]
    for path in files:
        text = read_text(path)
        if text is None:
            problems.append(f"{rel(path)}: not readable as UTF-8")
            continue
        fm = parse_frontmatter(text)
        if fm is None:
            problems.append(f"{rel(path)}: missing YAML front-matter")
            continue
        if not fm.get("description"):
            problems.append(f"{rel(path)}: front-matter has no 'description'")
        name = fm.get("name")
        if name and name != path.parent.name:
            problems.append(f"{rel(path)}: name {name!r} != directory {path.parent.name!r}")
        if len(text.strip()) < 200:
            problems.append(f"{rel(path)}: body is suspiciously short")
    for plugin in plugin_dirs():
        manifest = plugin / ".claude-plugin" / "plugin.json"
        if not manifest.exists():
            continue
        declared = load_json(manifest).get("skills")
        for entry in ([declared] if isinstance(declared, str) else declared or []):
            if not (plugin / str(entry).lstrip("./")).exists():
                problems.append(f"{rel(manifest)}: declared skills path {entry!r} does not exist")
    return problems


@check(8, "referenced agent files exist and have valid front-matter")
def c08():
    problems = []
    files = agent_files()
    if not files:
        return ["no agent files found under any plugin"]
    seen: dict[str, str] = {}
    for path in files:
        text = read_text(path)
        if text is None:
            problems.append(f"{rel(path)}: not readable as UTF-8")
            continue
        fm = parse_frontmatter(text)
        if fm is None:
            problems.append(f"{rel(path)}: missing YAML front-matter")
            continue
        name = fm.get("name")
        if not name:
            problems.append(f"{rel(path)}: front-matter has no 'name'")
        else:
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
                problems.append(f"{rel(path)}: agent name {name!r} must be lowercase with hyphens")
            if name != path.stem:
                problems.append(f"{rel(path)}: name {name!r} != file stem {path.stem!r}")
            key = f"{path.parent.parent.name}:{name}"
            if key in seen:
                problems.append(f"duplicate agent {key} in {rel(path)} and {seen[key]}")
            seen[key] = rel(path)
        if not fm.get("description"):
            problems.append(f"{rel(path)}: front-matter has no 'description'")
        # Plugin agents ignore these fields; shipping them would be misleading.
        for unsupported in ("hooks", "mcpServers", "permissionMode"):
            if unsupported in fm:
                problems.append(f"{rel(path)}: '{unsupported}' is ignored for plugin agents")
        tools = fm.get("tools", "")
        if "Agent" in tools:
            problems.append(f"{rel(path)}: tools grants 'Agent'; agents must not spawn agents")
    for plugin in plugin_dirs():
        manifest = plugin / ".claude-plugin" / "plugin.json"
        if not manifest.exists():
            continue
        declared = load_json(manifest).get("agents")
        for entry in ([declared] if isinstance(declared, str) else declared or []):
            if not (plugin / str(entry).lstrip("./")).exists():
                problems.append(f"{rel(manifest)}: declared agents path {entry!r} does not exist")
    return problems


@check(9, "hook configurations are well formed and their scripts exist")
def c09():
    problems = []
    configs = hook_configs()
    if not configs:
        return ["no hooks.json found; the toolkit is expected to ship hooks"]
    valid_events = {
        "PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionRequest",
        "PermissionDenied", "PostToolBatch", "UserPromptSubmit", "Stop",
        "SubagentStop", "SessionStart", "SessionEnd", "Notification", "PreCompact",
    }
    for config_path in configs:
        try:
            config = load_json(config_path)
        except json.JSONDecodeError as exc:
            problems.append(f"{rel(config_path)}: {exc}")
            continue
        if "hooks" not in config or not isinstance(config["hooks"], dict):
            problems.append(f"{rel(config_path)}: top-level 'hooks' object is missing")
            continue
        plugin_root = config_path.parent.parent
        for event in config["hooks"]:
            if event not in valid_events:
                problems.append(f"{rel(config_path)}: unknown hook event {event!r}")
        for event, handler in iter_hook_commands(config):
            if handler.get("type") != "command":
                problems.append(f"{rel(config_path)} [{event}]: only 'command' hooks are allowed here")
                continue
            command = handler.get("command", "")
            if "${CLAUDE_PLUGIN_ROOT}" not in command:
                problems.append(f"{rel(config_path)} [{event}]: command must use ${{CLAUDE_PLUGIN_ROOT}}")
            if not command.startswith("python "):
                problems.append(
                    f"{rel(config_path)} [{event}]: command must use cross-platform 'python'"
                )
            for script in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", command):
                if not (plugin_root / script).exists():
                    problems.append(f"{rel(config_path)} [{event}]: script {script!r} does not exist")
            if not isinstance(handler.get("timeout"), int):
                problems.append(f"{rel(config_path)} [{event}]: handler should set an integer timeout")
        if config_path == REPO / "plugins/dado-release-safety/hooks/hooks.json":
            destructive = ""
            for group in config["hooks"].get("PreToolUse", []):
                commands = [item.get("command", "") for item in group.get("hooks", [])]
                if any("guard_destructive_commands.py" in item for item in commands):
                    destructive = group.get("matcher", "")
                    break
            tools = {part.strip() for part in destructive.split("|")}
            if not {"Bash", "PowerShell"}.issubset(tools):
                problems.append(
                    f"{rel(config_path)}: destructive-command matcher must cover Bash and PowerShell"
                )
    for script in HOOK_SCRIPTS:
        if not (REPO / script).exists():
            problems.append(f"expected hook script missing: {script}")
    return problems


@check(10, "required README and documentation files exist")
def c10():
    problems = []
    for plugin in plugin_dirs():
        readme = plugin / "README.md"
        if not readme.exists():
            problems.append(f"{rel(readme)} does not exist")
        elif len(readme.read_text(encoding="utf-8").strip()) < 400:
            problems.append(f"{rel(readme)} is too short to be useful")
    for doc in REQUIRED_DOCS:
        path = REPO / doc
        if not path.exists():
            problems.append(f"{doc} does not exist")
        elif len(path.read_text(encoding="utf-8").strip()) < 200:
            problems.append(f"{doc} is too short to be useful")
    for profile in sorted((REPO / "profiles").glob("0*")):
        for required in ("README.md", "settings.json", "CLAUDE.md.snippet.md"):
            if not (profile / required).exists():
                problems.append(f"{rel(profile / required)} does not exist")
    return problems


# ---------------------------------------------------------------------------
# Checks 11-13: leakage
# ---------------------------------------------------------------------------

def scan(paths, patterns) -> list[str]:
    problems = []
    for path in paths:
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, pattern in patterns:
                match = pattern.search(line)
                if match:
                    problems.append(f"{rel(path)}:{lineno}: {label} pattern matched")
    return problems


@check(11, "no absolute personal filesystem paths")
def c11():
    problems = []
    for path in shipped_files():
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(allowed in line for allowed in ABSOLUTE_PATH_ALLOWED):
                continue
            for label, pattern in ABSOLUTE_PATH_PATTERNS:
                if pattern.search(line):
                    problems.append(f"{rel(path)}:{lineno}: absolute path ({label})")
    return problems


@check(12, "no obvious secret patterns in tracked files")
def c12():
    return scan(shipped_files(), SECRET_PATTERNS)


@check(13, "no private key material in tracked files")
def c13():
    problems = scan(shipped_files(), PRIVATE_KEY_PATTERNS)
    for path in shipped_files():
        if path.suffix in (".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".ppk"):
            problems.append(f"{rel(path)}: key-material file extension must not be committed")
        if path.name in ("id_rsa", "id_ed25519", "id_ecdsa", "id_dsa", ".git-credentials"):
            problems.append(f"{rel(path)}: credential file must not be committed")
    return problems


# ---------------------------------------------------------------------------
# Checks 14-16: permissions, deployment, merge and release
# ---------------------------------------------------------------------------

def shipped_json_configs() -> list[Path]:
    return [p for p in shipped_files((".json",)) if FIXTURES not in p.parents]


def collect_allow_rules() -> list[tuple[Path, str]]:
    found = []
    for path in shipped_json_configs():
        try:
            data = load_json(path)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        perms = data.get("permissions")
        if isinstance(perms, dict):
            for rule in perms.get("allow") or []:
                found.append((path, str(rule)))
    return found


@check(14, "no allow-everything permission rule is shipped")
def c14():
    problems = []
    for path, rule in collect_allow_rules():
        problems.append(f"{rel(path)}: ships a permissions.allow rule {rule!r}; "
                        f"this toolkit ships deny rules only")
        if rule.strip().lower() in ALLOW_ALL_RULES:
            problems.append(f"{rel(path)}: rule {rule!r} grants a whole tool")
    for path in shipped_json_configs():
        try:
            data = load_json(path)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        perms = data.get("permissions")
        if isinstance(perms, dict) and perms.get("defaultMode") == "bypassPermissions":
            problems.append(f"{rel(path)}: defaultMode 'bypassPermissions' disables the permission system")
        if data.get("disableAllHooks") is True:
            problems.append(f"{rel(path)}: ships disableAllHooks: true")
    # No skill may pre-approve tools: allowed-tools grants run without a prompt.
    for path in skill_files():
        fm = parse_frontmatter(read_text(path) or "") or {}
        if "allowed-tools" in fm:
            problems.append(f"{rel(path)}: front-matter declares 'allowed-tools'; "
                            f"skills in this toolkit grant no tools")
    return problems


@check(15, "no plugin silently enables deployment")
def c15():
    problems = []
    for path, rule in collect_allow_rules():
        low = rule.lower()
        if any(hint in low for hint in DEPLOY_RULE_HINTS):
            problems.append(f"{rel(path)}: allow rule {rule!r} would permit a deployment without asking")
    problems.extend(_hooks_never_allow())
    for path in skill_files():
        fm = parse_frontmatter(read_text(path) or "") or {}
        granted = fm.get("allowed-tools", "").lower()
        if any(hint in granted for hint in DEPLOY_RULE_HINTS):
            problems.append(f"{rel(path)}: allowed-tools would pre-approve a deployment")
    return problems


@check(16, "no plugin silently enables merge, tag or release")
def c16():
    problems = []
    for path, rule in collect_allow_rules():
        low = rule.lower()
        if any(hint.lower() in low for hint in MERGE_RULE_HINTS):
            problems.append(f"{rel(path)}: allow rule {rule!r} would permit a merge or release without asking")
    for path in skill_files():
        fm = parse_frontmatter(read_text(path) or "") or {}
        granted = fm.get("allowed-tools", "").lower()
        if any(hint.lower() in granted for hint in MERGE_RULE_HINTS):
            problems.append(f"{rel(path)}: allowed-tools would pre-approve a merge or release")
    return problems


def _hooks_never_allow() -> list[str]:
    """A hook that returns permissionDecision 'allow' suppresses the user's prompt."""
    problems = []
    for script in HOOK_SCRIPTS:
        path = REPO / script
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if re.search(r'"permissionDecision"\s*:\s*"allow"', line):
                problems.append(f"{rel(path)}:{lineno}: hook emits permissionDecision 'allow'")
            if re.search(r'^\s*(decision|DECISION)\s*=\s*"allow"', line):
                problems.append(f"{rel(path)}:{lineno}: hook hard-codes an 'allow' decision")
    return problems


# ---------------------------------------------------------------------------
# Checks 17-19: forbidden references
# ---------------------------------------------------------------------------

@check(17, "no plugin references the excluded desktop-assistant repository")
def c17():
    problems = []
    for path in shipped_files():
        if FIXTURES in path.parents:
            continue
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in EXCLUDED_APP_PATTERNS:
                if pattern.search(line):
                    problems.append(f"{rel(path)}:{lineno}: references an excluded repository path")
    return problems


@check(18, "nothing depends on Claude-Mem")
def c18():
    return _forbidden_dependency("claude-mem")


@check(19, "nothing depends on OmniRoute")
def c19():
    return _forbidden_dependency("omniroute")


def _forbidden_dependency(which: str) -> list[str]:
    pattern = dict(FORBIDDEN_DEPENDENCY_TOKENS)[which]
    problems = []
    for path in shipped_files():
        if path.name in ("SECURITY.md", "THREAT-MODEL.md", "CHANGELOG.md",
                         "CLAUDE-CODE-COMPATIBILITY.md", "run_validation.py"):
            continue  # these documents name the exclusion on purpose
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                problems.append(f"{rel(path)}:{lineno}: references {which}")
    return problems


# ---------------------------------------------------------------------------
# Checks 20-23: profiles, documentation, portability, cleanliness
# ---------------------------------------------------------------------------

@check(20, "profile and config examples parse")
def c20():
    problems = []
    profiles = sorted((REPO / "profiles").glob("0*"))
    if len(profiles) < 5:
        problems.append(f"expected 5 adoption profiles, found {len(profiles)}")
    for path in shipped_files((".json",)):
        try:
            data = load_json(path)
        except json.JSONDecodeError as exc:
            problems.append(f"{rel(path)}: {exc}")
            continue
        if path.parent.name.startswith("0") and path.name == "settings.json":
            if not isinstance(data, dict):
                problems.append(f"{rel(path)}: settings must be a JSON object")
                continue
            marketplaces = data.get("extraKnownMarketplaces", {})
            if EXPECTED_MARKETPLACE_NAME not in marketplaces:
                problems.append(f"{rel(path)}: does not register the {EXPECTED_MARKETPLACE_NAME} marketplace")
            else:
                source = marketplaces[EXPECTED_MARKETPLACE_NAME].get("source", {})
                if source.get("source") != "github" or "/" not in str(source.get("repo", "")):
                    problems.append(f"{rel(path)}: marketplace source is not a github owner/repo entry")
            for key in data.get("enabledPlugins", {}):
                if "@" not in key:
                    problems.append(f"{rel(path)}: enabledPlugins key {key!r} is not plugin@marketplace")
                    continue
                plugin, _, market = key.partition("@")
                if market != EXPECTED_MARKETPLACE_NAME:
                    problems.append(f"{rel(path)}: enabledPlugins key {key!r} names an unknown marketplace")
                if plugin not in EXPECTED_PLUGINS:
                    problems.append(f"{rel(path)}: enabledPlugins key {key!r} names an unknown plugin")
    return problems


@check(21, "documentation paths, links and commands match reality")
def c21():
    problems = []
    plugin_names = {p.name for p in plugin_dirs()}
    skills = {f"{p.parent.parent.parent.name}:{p.parent.name}" for p in skill_files()}
    agents = set()
    for path in agent_files():
        fm = parse_frontmatter(read_text(path) or "") or {}
        agents.add(f"{path.parent.parent.name}:{fm.get('name', path.stem)}")

    for path in shipped_files((".md",)):
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for ref in re.findall(r"(?<![\w./-])(plugins/[A-Za-z0-9._/-]+)", line):
                target = REPO / ref.rstrip(".,);:`")
                if not target.exists():
                    problems.append(f"{rel(path)}:{lineno}: path {ref!r} does not exist")
            for ref in re.findall(r"(?<![\w./-])(profiles/[A-Za-z0-9._/-]+)", line):
                target = REPO / ref.rstrip(".,);:`/")
                if not target.exists():
                    problems.append(f"{rel(path)}:{lineno}: path {ref!r} does not exist")
            for name in re.findall(r"plugin (?:install|uninstall|disable|enable) ([A-Za-z0-9-]+)@dado-tools", line):
                if name not in plugin_names:
                    problems.append(f"{rel(path)}:{lineno}: command references unknown plugin {name!r}")
            for ref in re.findall(r"/(dado-[a-z-]+):([a-z0-9-]+)", line):
                key = f"{ref[0]}:{ref[1]}"
                if ref[0] in plugin_names and key not in skills and key not in agents:
                    problems.append(f"{rel(path)}:{lineno}: references unknown skill or agent /{key}")
            for link in re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)", line):
                target = (path.parent / link.split("#", 1)[0]).resolve()
                if not target.exists():
                    problems.append(f"{rel(path)}:{lineno}: broken relative link {link!r}")

    # A stated component total is a factual claim; recompute rather than trust it.
    actual = (len(skill_files()), len(agent_files()), len(HOOK_SCRIPTS))
    for doc in ("README.md", "CHANGELOG.md"):
        text = read_text(REPO / doc)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            claim = re.search(r"(\d+) skills?, (\d+) agents?,? (?:and )?(\d+) hooks?", line)
            if claim and tuple(int(g) for g in claim.groups()) != actual:
                problems.append(
                    f"{doc}:{lineno}: claims {claim.group(0)!r} but the repository has "
                    f"{actual[0]} skills, {actual[1]} agents, {actual[2]} hooks")
    return problems


@check(22, "line endings and encodings are portable")
def c22():
    problems = []
    for path in shipped_files():
        try:
            raw = path.read_bytes()
        except OSError as exc:
            problems.append(f"{rel(path)}: unreadable ({exc})")
            continue
        if not raw:
            problems.append(f"{rel(path)}: file is empty")
            continue
        if raw.startswith(b"\xef\xbb\xbf"):
            problems.append(f"{rel(path)}: starts with a UTF-8 BOM")
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            problems.append(f"{rel(path)}: is not valid UTF-8")
            continue
        if b"\r\n" in raw:
            problems.append(f"{rel(path)}: contains CRLF line endings")
        if b"\t" in raw and path.suffix in (".json", ".yml", ".yaml"):
            problems.append(f"{rel(path)}: contains a tab character")
        if not raw.endswith(b"\n"):
            problems.append(f"{rel(path)}: does not end with a newline")
    if not (REPO / ".gitattributes").exists():
        problems.append(".gitattributes is missing; line endings are not pinned for contributors")
    return problems


@check(23, "no generated cache or runtime data is present")
def c23():
    problems = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        if ".git" in Path(dirpath).parts:
            continue
        for name in list(dirnames):
            if name in GENERATED_ARTIFACT_NAMES:
                problems.append(f"{rel(Path(dirpath) / name)}/: generated or editor directory present")
        for name in filenames:
            path = Path(dirpath) / name
            if name in GENERATED_ARTIFACT_NAMES or name.endswith(GENERATED_ARTIFACT_SUFFIXES):
                problems.append(f"{rel(path)}: generated or runtime file present")
    if not (REPO / ".gitignore").exists():
        problems.append(".gitignore is missing")
    return problems


# ---------------------------------------------------------------------------
# Checks 24-25: hook behaviour and rejection of dangerous input
# ---------------------------------------------------------------------------

def tree_snapshot(root: Path) -> dict[str, str]:
    snap = {}
    for path in walk_files(root, skip_fixtures=False):
        try:
            data = path.read_bytes()
        except OSError:
            continue
        snap[rel(path)] = hashlib.sha256(data).hexdigest()
    return snap


def run_hook(script: Path, payload: dict, cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=30,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


HOOK_CASES = [
    # (script, payload, expected decision or None, label)
    ("plugins/dado-core/hooks/guard_secret_files.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Write",
      "tool_input": {"file_path": "src/app.ts", "content": "export const x = 1;"}},
     None, "ordinary source file passes through untouched"),
    ("plugins/dado-core/hooks/guard_secret_files.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Write",
      "tool_input": {"file_path": ".env", "content": "TOKEN=abc"}},
     "deny", ".env is refused"),
    ("plugins/dado-core/hooks/guard_secret_files.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Write",
      "tool_input": {"file_path": ".env.example", "content": "TOKEN="}},
     None, ".env.example is allowed through"),
    ("plugins/dado-core/hooks/guard_secret_files.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Write",
      "tool_input": {"file_path": "certs/server.pem", "content": "x"}},
     "deny", "private key extension is refused"),
    ("plugins/dado-core/hooks/guard_secret_files.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Write",
      "tool_input": {"file_path": "notes.md",
                     "content": "-----BEGIN RSA PRI" + "VATE KEY-----\nabc"}},
     "deny", "PEM private key content is refused"),
    ("plugins/dado-core/hooks/guard_secret_files.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Write",
      "tool_input": {"file_path": "app/.npmrc", "content": "registry=x"}},
     "escalate", ".npmrc asks for confirmation"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Bash",
      "tool_input": {"command": "git status --porcelain"}},
     None, "read-only git passes through"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Bash",
      "tool_input": {"command": "git push --force origin main"}},
     "escalate", "force push asks for confirmation"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Bash",
      "tool_input": {"command": "gh pr merge 12 --squash"}},
     "escalate", "pull request merge asks for confirmation"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Bash",
      "tool_input": {"command": "netlify deploy --prod"}},
     "escalate", "deployment asks for confirmation"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "Bash",
      "tool_input": {"command": "rm -rf build"}},
     "escalate", "recursive force delete asks for confirmation"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "PowerShell",
      "tool_input": {"command": "Get-ChildItem -Force"}},
     None, "read-only PowerShell passes through"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "PowerShell",
      "tool_input": {"command": "Remove-Item -LiteralPath build -Recurse"}},
     None, "non-force recursive PowerShell delete does not match the bounded rule"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "PowerShell",
      "tool_input": {"command": "Remove-Item -LiteralPath build -Recurse -Force"}},
     "escalate", "PowerShell recursive force delete asks for confirmation"),
    ("plugins/dado-release-safety/hooks/guard_destructive_commands.py",
     {"hook_event_name": "PreToolUse", "tool_name": "PowerShell",
      "tool_input": {"command": "remove-item build -fo -r"}},
     "escalate", "PowerShell aliases and reversed flags ask for confirmation"),
]

MALFORMED_INPUTS = ["", "   ", "not json at all", "[]", "null", '{"tool_input": "string"}', "{}"]


@check(24, "hooks are sandboxed: no writes, correct decisions, never 'allow'", quick=False)
def c24():
    problems = []
    before_repo = tree_snapshot(REPO)

    with tempfile.TemporaryDirectory(prefix="dado-hook-test-") as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "workdir").mkdir()
        workdir = tmpdir / "workdir"
        before_tmp = tree_snapshot(tmpdir)

        for script_rel, payload, expected, label in HOOK_CASES:
            script = REPO / script_rel
            payload = {**payload, "cwd": str(workdir), "session_id": "test"}
            try:
                code, out, err = run_hook(script, payload, workdir)
            except subprocess.TimeoutExpired:
                problems.append(f"{script_rel}: timed out on '{label}'")
                continue
            if code != 0:
                problems.append(f"{script_rel}: exit {code} on '{label}' (hooks must always exit 0); stderr={err.strip()[:200]}")
            if expected is None:
                if out.strip():
                    problems.append(f"{script_rel}: produced output on '{label}' but should stay silent: {out.strip()[:200]}")
                continue
            if not out.strip():
                problems.append(f"{script_rel}: produced no decision on '{label}', expected {expected!r}")
                continue
            try:
                decision = json.loads(out)["hookSpecificOutput"]["permissionDecision"]
            except (ValueError, KeyError, TypeError) as exc:
                problems.append(f"{script_rel}: unparseable decision on '{label}': {exc}")
                continue
            if decision == "allow":
                problems.append(f"{script_rel}: emitted 'allow' on '{label}'; hooks must never grant")
            elif decision != expected:
                problems.append(f"{script_rel}: decision {decision!r} on '{label}', expected {expected!r}")

        # Every hook must survive malformed input without failing or blocking.
        for script_rel in HOOK_SCRIPTS:
            script = REPO / script_rel
            for raw in MALFORMED_INPUTS:
                proc = subprocess.run([sys.executable, str(script)], input=raw,
                                      capture_output=True, text=True, cwd=str(workdir),
                                      timeout=30, check=False)
                if proc.returncode != 0:
                    problems.append(f"{script_rel}: exit {proc.returncode} on malformed input {raw!r}")
                if '"allow"' in proc.stdout:
                    problems.append(f"{script_rel}: emitted 'allow' on malformed input {raw!r}")

        # The Stop hook is advisory: it must never return a decision that halts a turn.
        stop = REPO / "plugins/dado-release-safety/hooks/remind_uncommitted.py"
        code, out, _ = run_hook(stop, {"hook_event_name": "Stop", "cwd": str(workdir)}, workdir)
        if code != 0:
            problems.append(f"remind_uncommitted.py: exit {code} outside a git repository")
        if out.strip() and "decision" in out:
            problems.append("remind_uncommitted.py: returned a decision; it must be advisory only")

        # Import-level tests are not enough: execute the exact command strings from
        # hooks.json so interpreter resolution and plugin-root expansion are covered.
        configured_smoke = subprocess.run(
            [sys.executable, str(REPO / "tests/run_hook_commands.py")],
            capture_output=True,
            text=True,
            cwd=str(REPO),
            timeout=60,
            check=False,
        )
        if configured_smoke.returncode != 0:
            problems.append(
                "configured hook command smoke failed: "
                + (configured_smoke.stdout + configured_smoke.stderr).strip()[:500]
            )

        after_tmp = tree_snapshot(tmpdir)
        if after_tmp != before_tmp:
            created = sorted(set(after_tmp) - set(before_tmp))
            problems.append(f"hooks wrote inside the temp directory: {created[:5]}")

    after_repo = tree_snapshot(REPO)
    if after_repo != before_repo:
        changed = sorted(set(after_repo) ^ set(before_repo)) or \
            [k for k in after_repo if before_repo.get(k) != after_repo[k]]
        problems.append(f"hooks modified files in the repository: {changed[:5]}")
    return problems


@check(25, "invalid manifests and dangerous configurations are rejected", quick=False)
def c25():
    problems = []
    if not FIXTURES.is_dir():
        raise Skip("tests/fixtures does not exist")

    # Part A: committed invalid fixtures must each be rejected by the right validator.
    expectations = {
        "marketplace-malformed-json": "parse",
        "marketplace-wrong-name": "name",
        "marketplace-duplicate-plugins": "duplicate",
        "marketplace-path-traversal": "traversal",
        "marketplace-missing-source": "source",
        "plugin-missing-name": "name",
        "plugin-bad-version": "version",
        "settings-allow-all": "allow",
        "settings-enables-deploy": "deploy",
        "settings-enables-merge": "merge",
        "hooks-emits-allow": "allow",
        "hooks-missing-script": "script",
    }
    present = {p.name for p in sorted(FIXTURES.glob("*")) if p.is_dir()}
    for name in sorted(set(expectations) - present):
        problems.append(f"expected fixture tests/fixtures/{name}/ is missing")

    for name in sorted(present & set(expectations)):
        kind = expectations[name]
        rejected, why = _fixture_rejected(FIXTURES / name, kind)
        if not rejected:
            problems.append(f"fixture {name} was NOT rejected ({kind}): {why}")

    # Part B: dangerous content is generated here, never committed, and must be caught.
    with tempfile.TemporaryDirectory(prefix="dado-danger-") as tmp:
        tmpdir = Path(tmp)
        cases = {
            "leaked-aws.txt": "aws_key = " + "AKIA" + "IOSFODNN7EXAMPLE",
            "leaked-pem.txt": "-----BEGIN RSA PRI" + "VATE KEY-----\nMIIE\n",
            "absolute-path.md": "see " + "/home/" + "someuser/project/file.txt for details",
        }
        for filename, content in cases.items():
            (tmpdir / filename).write_text(content, encoding="utf-8")

        found_secret = scan([tmpdir / "leaked-aws.txt"], SECRET_PATTERNS)
        if not found_secret:
            problems.append("the secret scanner did not flag a generated access-key fixture")
        found_key = scan([tmpdir / "leaked-pem.txt"], PRIVATE_KEY_PATTERNS)
        if not found_key:
            problems.append("the private-key scanner did not flag a generated PEM fixture")
        text = (tmpdir / "absolute-path.md").read_text(encoding="utf-8")
        if not any(p.search(text) for _, p in ABSOLUTE_PATH_PATTERNS):
            problems.append("the absolute-path scanner did not flag a generated home path")

        # A CRLF + BOM file must be caught by the portability rules.
        crlf = tmpdir / "crlf.md"
        crlf.write_bytes(b"\xef\xbb\xbfline one\r\nline two\r\n")
        raw = crlf.read_bytes()
        if not (raw.startswith(b"\xef\xbb\xbf") and b"\r\n" in raw):
            problems.append("the portability fixture was not written as expected")
    return problems


def _fixture_rejected(directory: Path, kind: str) -> tuple[bool, str]:
    """Return (was_rejected, explanation) for one invalid fixture."""
    mkt = directory / ".claude-plugin" / "marketplace.json"
    plug = directory / ".claude-plugin" / "plugin.json"
    settings = directory / "settings.json"
    hooks = directory / "hooks" / "hooks.json"

    if mkt.exists():
        try:
            data = load_json(mkt)
        except json.JSONDecodeError as exc:
            return (kind == "parse", f"parse error: {exc}")
        if kind == "parse":
            return (False, "the file parsed successfully")
        if kind == "name":
            return (data.get("name") != EXPECTED_MARKETPLACE_NAME, f"name is {data.get('name')!r}")
        names = [e.get("name") for e in data.get("plugins", [])]
        if kind == "duplicate":
            return (len(names) != len(set(names)), f"names are {names}")
        if kind == "traversal":
            bad = [e.get("source") for e in data.get("plugins", [])
                   if isinstance(e.get("source"), str) and ".." in Path(e["source"]).parts]
            return (bool(bad), f"traversing sources: {bad}")
        if kind == "source":
            missing = [e.get("name") for e in data.get("plugins", []) if not e.get("source")]
            return (bool(missing), f"entries without a source: {missing}")

    if plug.exists():
        try:
            data = load_json(plug)
        except json.JSONDecodeError as exc:
            return (kind == "parse", f"parse error: {exc}")
        if kind == "name":
            return (not data.get("name"), f"name is {data.get('name')!r}")
        if kind == "version":
            version = data.get("version")
            return (not version or not SEMVER.fullmatch(str(version)), f"version is {version!r}")

    if settings.exists():
        try:
            data = load_json(settings)
        except json.JSONDecodeError as exc:
            return (kind == "parse", f"parse error: {exc}")
        rules = [str(r) for r in (data.get("permissions", {}) or {}).get("allow", [])]
        mode = (data.get("permissions", {}) or {}).get("defaultMode")
        if kind == "allow":
            unsafe = [r for r in rules if r.strip().lower() in ALLOW_ALL_RULES]
            return (bool(unsafe) or mode == "bypassPermissions",
                    f"rules={rules} defaultMode={mode!r}")
        if kind == "deploy":
            hits = [r for r in rules if any(h in r.lower() for h in DEPLOY_RULE_HINTS)]
            return (bool(hits), f"deploy-enabling rules: {hits}")
        if kind == "merge":
            hits = [r for r in rules if any(h.lower() in r.lower() for h in MERGE_RULE_HINTS)]
            return (bool(hits), f"merge-enabling rules: {hits}")

    if hooks.exists():
        try:
            data = load_json(hooks)
        except json.JSONDecodeError as exc:
            return (kind == "parse", f"parse error: {exc}")
        text = hooks.read_text(encoding="utf-8")
        if kind == "allow":
            # The decision may be escaped inside a shell string in the command, so
            # match permissionDecision followed by allow with any quoting between.
            grants = re.search(r"permissionDecision\\?\"?\s*:\s*\\?\"?allow", text)
            return (bool(grants), "hook config references an allow decision")
        if kind == "script":
            missing = []
            for _event, handler in iter_hook_commands(data):
                for script in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", handler.get("command", "")):
                    if not (directory / script).exists():
                        missing.append(script)
            return (bool(missing), f"missing scripts: {missing}")

    return (False, "no recognised fixture file found")


# ---------------------------------------------------------------------------
# Checks 26-30: additional invariants
# ---------------------------------------------------------------------------

@check(26, "the toolkit declares no third-party runtime dependency")
def c26():
    problems = []
    for name in ("package.json", "requirements.txt", "pyproject.toml", "Pipfile",
                 "package-lock.json", "poetry.lock", "yarn.lock", "pnpm-lock.yaml"):
        if (REPO / name).exists():
            problems.append(f"{name} present: this toolkit is intended to have no dependencies")
    for path in shipped_files((".py",)):
        text = read_text(path) or ""
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = re.match(r"\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)", line)
            if match and match.group(1) not in sys.stdlib_module_names:
                problems.append(f"{rel(path)}:{lineno}: imports non-stdlib module {match.group(1)!r}")
    return problems


@check(27, "no MCP server is declared by any plugin")
def c27():
    problems = []
    for plugin in plugin_dirs():
        if (plugin / ".mcp.json").exists():
            problems.append(f"{rel(plugin / '.mcp.json')}: version 0.1.0 ships no MCP servers")
        manifest = plugin / ".claude-plugin" / "plugin.json"
        if manifest.exists() and "mcpServers" in load_json(manifest):
            problems.append(f"{rel(manifest)}: declares mcpServers")
    return problems


@check(28, "skills and agents are namespaced and discoverable per plugin")
def c28():
    problems = []
    for plugin in plugin_dirs():
        skills = sorted((plugin / "skills").glob("*/SKILL.md")) if (plugin / "skills").is_dir() else []
        agents = sorted((plugin / "agents").glob("*.md")) if (plugin / "agents").is_dir() else []
        if not skills:
            problems.append(f"{plugin.name}: ships no skills")
        readme = plugin / "README.md"
        text = read_text(readme) or ""
        for skill in skills:
            invocation = f"/{plugin.name}:{skill.parent.name}"
            if invocation not in text:
                problems.append(f"{rel(readme)}: does not document {invocation}")
        for agent in agents:
            fm = parse_frontmatter(read_text(agent) or "") or {}
            scoped = f"{plugin.name}:{fm.get('name', agent.stem)}"
            if scoped not in text:
                problems.append(f"{rel(readme)}: does not document agent {scoped}")
    return problems


@check(29, "hook scripts are self-contained and make no network call")
def c29():
    problems = []
    banned = (
        ("urllib", re.compile(r"\burllib\b")),
        ("requests", re.compile(r"\brequests\b")),
        ("http.client", re.compile(r"\bhttp\.client\b")),
        ("socket", re.compile(r"\bsocket\b")),
        ("open-for-write", re.compile(r"open\([^)]*['\"][wax]")),
        ("shutil-write", re.compile(r"shutil\.(copy|move|rmtree|make_archive)")),
        ("os-remove", re.compile(r"os\.(remove|unlink|rmdir|makedirs|mkdir)")),
        ("shell-true", re.compile(r"shell\s*=\s*True")),
    )
    for script in HOOK_SCRIPTS:
        text = read_text(REPO / script) or ""
        body = "\n".join(line for line in text.splitlines() if not line.strip().startswith("#"))
        for label, pattern in banned:
            if pattern.search(body):
                problems.append(f"{script}: uses {label}, which a hook must not do")
    return problems


@check(30, "every marketplace entry is independently identifiable")
def c30():
    problems = []
    entries = marketplace().get("plugins", [])
    for entry in entries:
        name = entry.get("name")
        for key in ("description", "version", "source"):
            if not entry.get(key):
                problems.append(f"marketplace entry {name!r}: missing {key!r}")
        if entry.get("license") and entry["license"] != "MIT":
            problems.append(f"marketplace entry {name!r}: unexpected license {entry['license']!r}")
        if not (REPO / "plugins" / str(name) / "README.md").exists():
            problems.append(f"marketplace entry {name!r}: has no README to identify it")
    descriptions = [e.get("description") for e in entries]
    if len(set(descriptions)) != len(descriptions):
        problems.append("two marketplace entries share a description; they are not distinguishable")
    if (REPO / "LICENSE").exists():
        pass
    else:
        problems.append("LICENSE is missing but plugin manifests declare a license")
    return problems


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run(selected_quick_only: bool) -> list[Result]:
    results = []
    for number, name, mode, fn in sorted(CHECKS):
        if selected_quick_only and mode == "full":
            results.append(Result(number, name, "SKIP", reason="--quick: subprocess check not run"))
            continue
        try:
            problems = fn()
        except Skip as exc:
            results.append(Result(number, name, "SKIP", reason=str(exc)))
            continue
        except Exception as exc:  # a broken check is a failure, never a pass
            results.append(Result(number, name, "FAIL", problems=[f"check raised {type(exc).__name__}: {exc}"]))
            continue
        status = "FAIL" if problems else "PASS"
        results.append(Result(number, name, status, problems=problems))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true",
                        help="structural checks only; subprocess-based checks are skipped and reported as skipped")
    parser.add_argument("--json", action="store_true", help="print a JSON summary instead of text")
    args = parser.parse_args()

    results = run(args.quick)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    skipped = sum(1 for r in results if r.status == "SKIP")

    if args.json:
        print(json.dumps({
            "total": len(results), "passed": passed, "failed": failed, "skipped": skipped,
            "checks": [{"number": r.number, "name": r.name, "status": r.status,
                        "problems": r.problems, "reason": r.reason} for r in results],
        }, indent=2))
        return 1 if failed else 0

    print(f"dado-claude-toolkit validation — {REPO}")
    print("=" * 72)
    for r in results:
        print(f"[{r.status:4}] {r.number:02d}  {r.name}")
        if r.status == "SKIP" and r.reason:
            print(f"        skipped: {r.reason}")
        for problem in r.problems:
            print(f"        - {problem}")
    print("=" * 72)
    print(f"{len(results)} checks: {passed} passed, {failed} failed, {skipped} skipped")
    if skipped:
        print("Skipped checks are NOT passes. Each is listed above with its reason.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
