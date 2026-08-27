# dado-content-localization

Factual writing, bilingual synchronization, CV consistency and metadata review — with
a hard rule against inventing claims about people or organisations.

- **Version:** 0.1.0
- **Marketplace:** `dado-tools`
- **Install:** `/plugin install dado-content-localization@dado-tools`
- **Depends on:** nothing. Pairs well with `dado-core` (honesty rules) and
  `dado-web-quality` (which checks metadata mechanics and points here for copy
  parity rather than duplicating it).

## The rule this plugin exists for

**Never invent a fact about a person or an organisation.** Not to fill a gap, not to
make a sentence flow, not because it is probably true.

Never invent: qualifications, education completion, certifications or their issuers,
employers, clients, job titles, seniority, responsibilities, dates, durations,
measurable results, percentages, awards, publications, ownership or founding claims,
client relationships, or language fluency.

When evidence is missing there are three options and only three: leave it out, use
wording that says only what is supported, or flag it for the user's confirmation.
Filling the gap with a plausible value is not one of them.

## Skills

| Skill | Invoke | What it covers |
| --- | --- | --- |
| Factual claims review | `/dado-content-localization:factual-claims-review` | Classify every claim as supported, inferred, unsupported or contradicted; catch quiet factual upgrades; recompute dates and derived numbers |
| Bilingual sync | `/dado-content-localization:bilingual-sync` | EN/ME structural and substance parity, protected terms verbatim in both, per-language quality, `hreflang` and switcher behaviour |
| CV consistency | `/dado-content-localization:cv-consistency` | Role order, dates, education, certifications and titles across web, PDF, print layout, structured data and metadata; `pdftotext` extraction |
| Copy quality | `/dado-content-localization:copy-quality` | Remove generic AI-sounding and repetitive copy without changing a single claim or touching approved wording |
| Content diff review | `/dado-content-localization:content-diff-review` | Word-level before/after comparison; frozen-set violations, accidental location changes, forbidden-copy regressions, metadata drift |

## Agents

| Agent | Tools | Responsibility |
| --- | --- | --- |
| `dado-content-localization:content-fact-checker` | Read, Grep, Glob, Bash | Every claim against an approved source |
| `dado-content-localization:bilingual-reviewer` | Read, Grep, Glob, Bash | Parity between two language versions |

No hooks. Neither agent can spawn further agents.

## Templates

| File | Copy it to | Purpose |
| --- | --- | --- |
| `templates/protected-terms.example.json` | `.claude/dado-protected-terms.json` | Protected organisation names, job titles, certifications, factual strings, locations; the `forbiddenCopy` list; the surfaces where facts appear |
| `templates/CONTENT-FACTS.template.md` | `docs/ai/CONTENT-FACTS.md` | The single approved source for factual claims: identity, roles, education, certifications, measurable claims, and an explicit "known gaps — do not fill these in" section |

Both ship as **placeholders only** (`<Official Organisation Name>`,
`<Exact Approved Job Title>`). No real personal data, no CV content and no project
content is embedded in this plugin. Nothing reads these files automatically — they are
written agreements the skills read when you point them at them.

Both files are committed in whatever project you copy them into. In a public
repository they are world-readable, so they must contain only what the owner has
agreed to publish: no credentials, no private contact details, no third-party
personal data, no absolute local paths.

## Uninstall

```
/plugin uninstall dado-content-localization@dado-tools
```

The plugin creates no files in your repository. Templates you copied into a project
are yours and stay until you delete them.
