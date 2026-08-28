# Profile 04 — bilingual, content-heavy website

For a site whose value is its content, published in two languages — English and
Montenegrin in the examples, but the plugin is not limited to that pair. Use it where
the expensive mistakes are factual and editorial, not structural.

## Plugins

| Plugin | Why |
| --- | --- |
| `dado-core` | Orientation, safe editing, honest reporting |
| `dado-content-localization` | Factual claims, EN/ME parity, CV consistency, copy quality, content diffs |
| `dado-web-quality` | Metadata mechanics, `hreflang`, routing, layout, accessibility |
| `dado-ui-design` | Visual direction, typography, interaction, responsive hierarchy and design-system guidance |

The two content plugins divide the work deliberately: `dado-web-quality` checks that
`hreflang` is reciprocal and the metadata exists; `dado-content-localization` checks
that what it says is true and matches the other language.

## Install

```bash
claude plugin marketplace add Dado211207/dado-claude-toolkit
claude plugin install dado-core@dado-tools
claude plugin install dado-content-localization@dado-tools
claude plugin install dado-web-quality@dado-tools
claude plugin install dado-ui-design@dado-tools
```

## Files to copy

| From | To | Note |
| --- | --- | --- |
| `settings.json` | `.claude/settings.json` | Merge by hand if one exists |
| `CLAUDE.md.snippet.md` | append to `CLAUDE.md` | |
| `plugins/dado-content-localization/templates/protected-terms.example.json` | `.claude/dado-protected-terms.json` | **Fill in your real terms** |
| `plugins/dado-content-localization/templates/CONTENT-FACTS.template.md` | `docs/ai/CONTENT-FACTS.md` | **Fill in with the owner** |
| `plugins/dado-web-quality/config/web-quality.config.example.json` | `.claude/dado-web-quality.json` | Set the languages and routes |

The two content files are the ones that make this profile work. Without an approved
source of facts, every claim is unsupported and every review ends in questions.

> Both files are committed. In a public repository they are world-readable. Put only
> publishable information in them: no credentials, no private contact details, no
> third-party personal data, no absolute local paths.

## Required tools

| Tool | Needed for | If missing |
| --- | --- | --- |
| Node + the project's package manager | Build, dev server | Nothing runs |
| `pdftotext` (poppler-utils) | Verifying a generated PDF's actual text | The PDF is reported **unverified** — never substitute the HTML source |
| `git` word-diff | Content diff review | Line diffs hide which two words changed |
| Playwright | Rendered checks, print layout | Those checks are `not-run` |

## Suggested verification commands

```bash
npm run build

# content diffs — word level, not line level
git diff --word-diff=color -- <content paths>

# PDF must be compared as extracted text, not as its source
pdftotext -layout public/cv-en.pdf - > /tmp/cv-en.txt
diff -u /tmp/cv-en.prev.txt /tmp/cv-en.txt

# protected terms must still be present, verbatim
grep -rnF "<protected string>" <content paths>

# forbidden copy must have zero matches
grep -rnF "<forbidden string>" <content paths> && echo "REGRESSION" || echo "clean"

# hreflang reciprocity and metadata
curl -s https://<url>/en/<page> | grep -i 'hreflang\|canonical\|og:'
curl -s https://<url>/me/<page> | grep -i 'hreflang\|canonical\|og:'
```

## What remains manual

- Filling in `docs/ai/CONTENT-FACTS.md` and `.claude/dado-protected-terms.json`. Only
  the owner can approve a fact.
- **Confirming every flagged claim.** The plugin's job is to flag, not to resolve.
- Native-speaker judgement on the second language. A flagged sentence you fix is
  better than fluent text nobody checked.
- Deciding which version is right when two sources contradict each other.
- Every deploy.

## The rule this profile enforces

Never invent a qualification, employer, client, job title, responsibility, date,
measurable result, award, certification issuer, ownership claim or language level.
When evidence is missing: leave it out, use conservative wording, or flag it. Never
fill the gap with a plausible value.

Watch the quiet upgrades too — "assisted with" → "led", "studied" → "graduated",
"developer" → "senior developer". Each is a factual change wearing an editing
disguise.

## Remove it cleanly

```bash
claude plugin uninstall dado-content-localization@dado-tools
claude plugin uninstall dado-web-quality@dado-tools
claude plugin uninstall dado-ui-design@dado-tools
claude plugin uninstall dado-core@dado-tools
claude plugin marketplace remove dado-tools     # optional
```

Then remove the `extraKnownMarketplaces` and `enabledPlugins` blocks from
`.claude/settings.json` and the snippet from `CLAUDE.md`.

Keep `docs/ai/CONTENT-FACTS.md` and `.claude/dado-protected-terms.json`. They are
your records of what is approved, and they are useful whether or not the plugin is
installed.
