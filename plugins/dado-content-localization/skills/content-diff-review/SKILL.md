---
name: content-diff-review
description: Compare content before and after an edit to catch accidental changes to facts, names, locations, titles and protected wording, including drift between visible copy and metadata. Use after any content edit, before publishing copy changes, and when checking whether a previous edit silently altered a claim.
---

# Content diff review

The purpose of this pass is to catch the changes nobody intended. Most content
damage is not a wrong rewrite; it is a correct-looking rewrite that changed a fact on
the way past.

## 1. Get a real diff

```
git diff -- <content paths>
git diff --word-diff=color -- <content paths>
```

Word-diff is the important one for prose: a line diff shows a whole paragraph as
changed and hides which two words moved.

For a rendered comparison (HTML, PDF), extract the text from both versions first and
diff the extractions, not the markup:

```
pdftotext -layout old.pdf - > /tmp/old.txt
pdftotext -layout new.pdf - > /tmp/new.txt
diff -u /tmp/old.txt /tmp/new.txt
```

If a tool is unavailable, say so and mark that surface **unverified** rather than
assuming it matches its source.

## 2. Check the frozen set first

Before reading the diff for quality, check that nothing in the frozen set changed:

| Category | Check |
| --- | --- |
| Official organisation names | Byte-for-byte identical |
| Exact job titles | Byte-for-byte identical |
| Certification and issuer names | Byte-for-byte identical |
| Approved factual strings | Byte-for-byte identical |
| Dates and date ranges | Identical unless the change was requested |
| Numbers and measurements | Identical unless the change was requested |
| Locations | Identical — see below |
| Contact details, URLs | Identical unless requested |

Load the project's protected terms file (from
`${CLAUDE_PLUGIN_ROOT}/templates/protected-terms.example.json`) and grep for each
entry in the new content. A protected string that no longer appears is a finding even
if nothing obviously replaced it.

## 3. Locations, specifically

Accidental location changes are common and consequential: a city changed by an
autocomplete, a country name normalised by a rewrite, a region swapped for the
country, or a location that is right in one language version and wrong in the other.

Grep both versions for every place name and compare the sets. Any place that appears
in one and not the other, or that changed form, is a finding — even a "harmless"
normalisation.

## 4. Forbidden copy regressions

Some wording was removed deliberately: a previous employer, a superseded title, an
old product name, a wrong location, a claim that was withdrawn. It must not come
back — and it comes back most often through a copy-paste from an old file, a
reverted section, or a translation made from a stale source.

Grep the new content for every entry in the project's `forbiddenCopy` list. Zero
matches is the only acceptable result.

## 5. Metadata versus visible copy

After a content edit, check that these still agree with the body:

- `<title>` and meta description
- Open Graph and Twitter title and description
- JSON-LD fields (`jobTitle`, `worksFor`, `alumniOf`, `hasCredential`, `address`)
- any summary of this content that appears on another page
- the PDF version, if the content also exists as one

A body updated and a metadata block left behind is the most common post-edit defect,
and the one most likely to be quoted by a search engine.

## 6. Cross-language drift

For bilingual content, run the diff on both languages and compare the *shapes* of the
two diffs. If one language changed and the other did not, the versions have drifted —
report it rather than translating the change across, since that publishes wording the
user has not approved.

## 7. Report

```
Files:        <what was diffed, and how (word-diff, extracted text)>
Frozen set:   intact | VIOLATED: <term> was <old>, now <new>
Locations:    unchanged | CHANGED: <old> -> <new>
Forbidden:    none present | PRESENT: <string> at <file>:<line>
Facts:        unchanged | CHANGED: <claim> — intended? <yes/no>
Metadata:     consistent with body | STALE: <field> still says <old>
Languages:    both updated | ONLY <lang> changed
Unverified:   <surfaces you could not extract or compare>
```

Any line that is not the clean outcome needs the user's decision before publishing.
Do not "fix" a frozen-set violation by choosing which version is right.
