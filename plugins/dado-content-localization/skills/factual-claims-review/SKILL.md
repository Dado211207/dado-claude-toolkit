---
name: factual-claims-review
description: Check every factual claim in content against evidence and refuse to invent qualifications, employers, dates, results, awards or relationships. Use before publishing or editing any biography, CV, about page, case study, structured data or marketing copy that states a fact about a person or organisation.
---

# Factual claims review

The hard rule: **never invent a fact about a person or an organisation.** Not to fill
a gap, not to make a sentence flow, not because it is probably true, not because a
similar page says it.

## Never invent, under any circumstances

- qualifications, degrees, diplomas, or whether education was completed
- certifications, their issuers, their levels, or their validity dates
- employers, clients, partners, or a relationship with any of them
- job titles, seniority, team size, or reporting lines
- responsibilities the person did not state
- employment dates, durations, or the order of roles
- measurable results: percentages, revenue, user counts, performance gains, rankings
- awards, recognitions, publications, speaking engagements
- ownership, founding, or equity in anything
- languages spoken and the level of fluency
- locations lived in or worked in

If evidence is missing, you have three options and only three:

1. **Leave it out.** Usually the right answer.
2. **Use conservative wording** that says only what is supported.
3. **Mark it for the user** with an explicit placeholder and a question.

Never fill the gap with a plausible value.

## Classify every claim

Go through the content claim by claim and label each one:

| Label | Meaning | What to do |
| --- | --- | --- |
| **Supported** | An approved source states it | Keep. Cite the source in your report |
| **Inferred** | It follows from supported facts | Rewrite so the inference is visible, or drop it |
| **Unsupported** | No source states it | Flag for the user; do not publish it |
| **Contradicted** | Two sources disagree | Report both; change nothing until the user decides |

An approved source is: a file in the repository the user has approved, a document the
user provided, or something the user stated in this task. It is **not**: a similar
page elsewhere on the site, a previous draft, a search result, your own earlier
output, or a plausible pattern.

## Words that turn a fact into a claim you cannot support

Watch for quantifiers and superlatives added during editing:

- "leading", "award-winning", "top", "best", "renowned", "expert in"
- "over N years of experience" — check the arithmetic against the actual dates
- "increased X by N%" — a number with no source is a fabricated result
- "trusted by", "worked with" — implies a relationship that must be real
- "certified" — implies a specific credential from a specific issuer
- "specialising in" — fine if the person said so; not if you inferred it from a
  project list

Also watch the quiet ones: changing "assisted with" to "led", "contributed to" to
"built", "studied" to "graduated in". Each is a factual upgrade.

## Dates and arithmetic

- check every date range for overlaps and gaps that contradict other statements
- check that "N years of experience" matches the earliest start date
- check that role order in one place matches role order everywhere else
- check that a "present" role is still current

Recompute rather than trusting the existing text. An out-of-date "over 8 years"
becomes wrong on its own.

## Report

```
Supported:    <n> claims
Inferred:     <claim> — rests on <what> — <rewritten | dropped>
Unsupported:  <claim> — no source found — NEEDS USER CONFIRMATION
Contradicted: <claim> — <source A says X> vs <source B says Y> — unchanged
Arithmetic:   <what you recomputed and what it produced>
```

End with the list of questions the user must answer. Deliver the content with the
unsupported claims removed or conservatively worded, not with the gaps filled in.
