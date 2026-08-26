# Using the toolkit in GitHub Actions

The Claude Code GitHub Action (`anthropics/claude-code-action@v1`) installs plugins
through two inputs:

| Input | Value |
| --- | --- |
| `plugin_marketplaces` | Newline-separated marketplace **Git URLs** |
| `plugins` | Newline-separated `plugin-name@marketplace-name` |

The marketplace name comes from the marketplace manifest (`dado-tools`), not from the
repository URL.

## Example

```yaml
name: Review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: read
      id-token: write
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0        # the skills compare against a base commit
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          plugin_marketplaces: "https://github.com/Dado211207/dado-claude-toolkit.git"
          plugins: "dado-core@dado-tools"
          prompt: "/dado-core:verify-and-report"
```

Use `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}` instead if you
authenticate with a subscription token.

## Rules for a workflow that uses this toolkit

- **Least privilege.** Give the job the narrowest `permissions:` block that works.
  `contents: read` unless it genuinely must push.
- **Pin the marketplace** to a tag or commit for a workflow that matters, so a change
  here cannot alter your CI behaviour without a commit in your repository.
- **Pin actions** to a released major version at minimum; a commit SHA is stronger.
- **Do not grant merge or deploy.** Nothing in this toolkit performs one, and a
  workflow should not be the place you first hand that power to an agent.
- **`fetch-depth: 0`** if you want base-vs-head comparison; the default shallow clone
  has no base commit to diff against.
- **Tools must exist on the runner.** A skill cannot check what is not installed. An
  unavailable tool becomes a `not-run` line — which is the correct outcome, not a
  failure to hide.

## Repository skills instead of plugins

If you would rather not install a marketplace in CI, copy the skills you want into
the repository's `.claude/skills/` and invoke them unnamespaced after checkout:

```yaml
          prompt: "/verify-and-report"
```

Same trade-offs as vendoring for cloud sessions — see
[CLOUD-USAGE.md](CLOUD-USAGE.md).

## This repository's own workflow

`.github/workflows/validate.yml` runs the validation suite on pushes and pull
requests. It is deliberately minimal:

- `permissions: contents: read` and nothing else
- no secrets, no `ANTHROPIC_API_KEY`, no Claude Code action
- Ubuntu only — the suite is pure Python and platform-independent, so a second OS
  would add time without adding coverage
- runs `python3 tests/run_validation.py` **twice**, and runs
  `claude plugin validate .` only if the CLI happens to be present, reporting it as
  skipped when it is not

It publishes nothing, deploys nothing, and opens or merges no pull request.
