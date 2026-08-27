---
name: bilingual-sync
description: Keep two language versions of a site or document in sync in substance while preserving official names, exact titles and protected wording verbatim in both. Use when editing bilingual content such as English and Montenegrin, adding a section to one language, or checking whether translations have drifted apart.
---

# Bilingual synchronization

Two language versions must say the same things. They must not say them in the same
words — and some words must not change at all.

## 1. Structural parity

Compare the two versions section by section:

- every section, heading, list item, card, link and call to action exists in both
- the order matches
- counts match: the same number of roles, projects, list entries, FAQ items
- links point to the corresponding language version of the target, not always to the
  default language
- images, alt text and captions exist in both
- metadata exists in both: `<title>`, description, Open Graph, structured data

A section present in one language and missing in the other is the most common defect
and the easiest to find. Do this pass first.

## 2. Substance parity

Then compare meaning, claim by claim. The two versions must not differ in:

- any factual claim — dates, titles, employers, qualifications, numbers
- what is offered, promised or stated
- names of organisations, products or places

If one version makes a claim the other does not, that is a defect regardless of which
is "the original". Report it; do not resolve it by translating the extra claim into
the other language, because that also publishes it in a language the user may not
have approved.

## 3. What must stay verbatim in both languages

Load the project's protected terms (see
`${CLAUDE_PLUGIN_ROOT}/templates/protected-terms.example.json`, copied into the
project and filled in). By default, treat these as untranslatable:

- **Official organisation names.** A registered legal name is a name, not a phrase.
  Do not translate it, do not reorder it, do not expand or contract an abbreviation.
- **Exact job titles** the user has approved. If the title is official in one
  language only, keep that form in both and add a translated gloss beside it only if
  the user has approved the gloss.
- **Certification and qualification names**, including the issuer's name.
- **Product and brand names.**
- **Approved factual strings** — sentences the user has signed off on word for word.

When a name genuinely has an official form in each language, both forms are protected
strings; use the right one per language and never invent a third.

## 4. Place names

Place names take the conventional form of the language being written, where one
exists. What must never happen is an accidental change of *which* place is meant.

Check every location against the source. A location that differs between the two
language versions, or that changed during an edit, is a factual defect — see
`/dado-content-localization:content-diff-review`.

## 5. Language quality, per language

Each version must read as if written in that language, not translated into it:

- no calques or word-for-word structures that are ungrammatical in the target
- correct grammatical agreement, case and diacritics — for Montenegrin, that includes
  the letters `š`, `đ`, `č`, `ć`, `ž`, and `ś`/`ź` where the project uses them
- consistent script if the project targets one
- dates, numbers and currency formatted per locale
- the same register in both versions: if one is formal, both are

Where you are not confident about the target language, say so rather than producing
confident text. A flagged sentence the user fixes is better than a fluent error.

## 6. Technical parity

- `<html lang>` is correct on each version
- `hreflang` entries are reciprocal in both directions, plus `x-default`
- the language switcher on any page links to the **same page** in the other language,
  not to that language's home page
- a URL that exists in one language has a counterpart, or the switcher handles the
  absence gracefully
- language choice persists sensibly and does not fight an explicit URL

## 7. Report

```
Structure:  <n> sections both | missing in <lang>: <list> | extra in <lang>: <list>
Substance:  <claim> — differs: <lang A says …> vs <lang B says …>
Protected:  <term> — <verbatim in both | ALTERED in <lang>: was <x>, now <y>>
Places:     <location> — <matches source | CHANGED>
Language:   <lang> — <issues, or "no issues found">
Technical:  lang attr <ok|…> | hreflang <reciprocal|…> | switcher <per-page|…>
Flagged:    <sentences needing a native check or user confirmation>
```
