# Invalid fixtures — do not copy any of this

Every file in this directory is **deliberately wrong**. They exist so that check 25
of `tests/run_validation.py` can prove the validators reject bad input, rather than
only proving they accept good input.

Nothing here is loaded by Claude Code, installed, or shipped to users. The validation
suite excludes this directory from every check that scans shipped files, and only
check 25 reads it.

| Fixture | What is wrong with it |
| --- | --- |
| `marketplace-malformed-json/` | Trailing comma; the JSON does not parse |
| `marketplace-wrong-name/` | Marketplace name is not `dado-tools` |
| `marketplace-duplicate-plugins/` | Two entries share the name `dado-core` |
| `marketplace-path-traversal/` | A `source` of `../../../etc` escapes the repository |
| `marketplace-missing-source/` | A plugin entry has no `source` |
| `plugin-missing-name/` | `plugin.json` has no `name` |
| `plugin-bad-version/` | `version` is `"latest"`, not a semantic version |
| `settings-allow-all/` | `permissions.allow` grants whole tools and sets `bypassPermissions` |
| `settings-enables-deploy/` | An allow rule would let a deployment run without asking |
| `settings-enables-merge/` | An allow rule would let a merge or release run without asking |
| `hooks-emits-allow/` | A hook returns `permissionDecision: "allow"`, suppressing the user's prompt |
| `hooks-missing-script/` | A hook command points at a script that does not exist |

## Why there are no secret fixtures here

A file containing a real-shaped credential — an access key, a token, a PEM private
key block — would be committed to a public repository, would be flagged by every
secret scanner that looks at it, and could be refused by push protection.

Those cases are therefore **generated at test time** into a temporary directory that
check 25 creates and deletes. The scanner is run against them there, so the rejection
is still proven, and nothing secret-shaped is ever committed.

The same applies to the encoding fixtures (BOM, CRLF): they would fail the
portability check on themselves, so they are generated rather than committed.
