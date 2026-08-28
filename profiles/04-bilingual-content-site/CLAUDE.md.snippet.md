<!-- Append to the project's CLAUDE.md. Edit the placeholders. -->

## Content rules

For a new page or material visual redesign, use `/dado-ui-design:ui-ux-pro-max`
before implementation. Its recommendations may change presentation, never approved
facts, protected terms or language parity.

### The approved source

`docs/ai/CONTENT-FACTS.md` is the single approved source for factual claims.
`.claude/dado-protected-terms.json` holds protected strings and the forbidden-copy
list. Read both before editing any content.

A claim not in the approved source is **unsupported**. Unsupported claims are flagged
for the owner — never published, never inferred, never filled in with a plausible
value.

### Never invent

Qualifications, education completion, certifications and their issuers, employers,
clients, job titles, seniority, responsibilities, dates, durations, measurable
results, percentages, awards, publications, ownership or founding claims, client
relationships, language fluency levels.

When evidence is missing there are three options and only three:

1. Leave it out.
2. Use wording that says only what is supported.
3. Flag it for the owner with an explicit question.

Watch for the quiet upgrades: "assisted with" → "led", "contributed to" → "built",
"studied" → "graduated", "developer" → "senior developer", and quantifiers that
arrived without a source ("leading", "award-winning", "over N years", "increased X by
N%", "certified", "trusted by").

### Languages

```
Default:   <en>
Supported: <en, me>
Parity required between: <en and me>
```

- Both versions must have the same sections, in the same order, with the same counts.
- Both versions must make the same factual claims.
- Protected strings — official organisation names, exact job titles, certification
  and issuer names, product names, approved sentences — appear **byte-for-byte** in
  both. They are never translated, reordered, abbreviated or expanded.
- Each version must read as written in its own language, not translated into it.
  Montenegrin diacritics (`š`, `đ`, `č`, `ć`, `ž`, and `ś`/`ź` where used) must be
  correct.
- Never resolve a difference by translating the extra content across — that publishes
  wording the owner has not approved. Report it instead.

### Surfaces where the same facts appear

```
Web:            <routes per language>
PDF:            <paths>
Structured data:<path to JSON-LD source>
Metadata:       <where titles and descriptions live>
```

Whatever is not on this list is the one that stays wrong. Check all of them.

### After every content edit

Run `/dado-content-localization:content-diff-review`, or do it by hand:

```bash
git diff --word-diff -- <content paths>
grep -rnF "<each protected string>" <content paths>   # must still be present
grep -rnF "<each forbidden string>" <content paths>   # must have zero matches
pdftotext -layout <pdf> - | diff -u - <previous extraction>
```

Check specifically for: changed locations, changed dates, changed titles, metadata
left stale after the body changed, and one language updated while the other was not.

If `pdftotext` is unavailable, report the PDF as **unverified**. Do not read the HTML
source and describe it as the PDF's content.

### Copy quality

Cut generic openers, stacked empty adjectives, hedged confidence, and the same verb
opening every list item. But: improving a sentence must never add, remove or alter a
factual claim, and protected wording is not yours to improve. If a rewrite would risk
a claim, leave it and flag it.

### Stop line

No deploy, merge, tag or release without an explicit instruction in the current task.
