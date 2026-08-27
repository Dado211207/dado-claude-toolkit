<!-- Append to the project's CLAUDE.md. Edit the placeholders. -->

## Working rules

Before changing anything, run `/dado-core:orient` — or do the same by hand: read this
file, identify the stack from the manifests that exist, and capture git state.

### Commands (the real ones for this project)

```
Build:     <command, or "none defined">
Test:      <command, or "none defined">
Lint:      <command, or "none defined">
Typecheck: <command, or "none defined">
```

Use these. Do not invent a command that is not listed here.

### Protected areas

Do not modify without being asked:

- files already carrying uncommitted changes that are unrelated to the current task
- lockfiles and generated files — regenerate them with the project's own tooling
- `.env*` and anything holding credentials — never read, never write, never print
- CI workflow permissions and branch protection
- `<add this project's protected paths>`

### Verification and reporting

- A check that did not run did not pass. Report every command as
  `<command> -> exit <code>  (<n> passed, <n> failed, <n> skipped)`.
- Skipped, cancelled and never-run are not passes. Say so explicitly.
- Never raise a timeout, add a retry, weaken an assertion or skip a test to turn a
  failure green. Measure the cause first.
- Separate fact (a file says it, or a command printed it) from inference and
  assumption. Cite the path or command for facts.
- Print the branch and full commit SHA before claiming any git state.

### Stop line

No merge, deployment, release, tag, package publish, destructive git operation or
repository-visibility change without an explicit instruction in the current task.

General permission to build or fix is not permission to merge or deploy. Neither is
a green CI run or an approving review.
