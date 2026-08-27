---
name: cv-consistency
description: Check that a CV is internally consistent and consistent across its formats - web page, PDF, print layout and metadata - covering role order, dates, education, certifications and titles. Use when editing a CV or resume, regenerating a PDF, or checking that a web CV and its downloadable version still agree.
---

# CV consistency

A CV usually exists in several places at once: a web page, a downloadable PDF, a
print stylesheet, structured data, and page metadata. They drift. Every drift is a
factual contradiction someone may notice at the worst moment.

## 1. Enumerate the surfaces

List every place the same information appears:

- the web CV route(s), one per language
- the PDF, one per language
- the print stylesheet (`@media print`) rendering of the web page
- JSON-LD structured data
- `<title>`, meta description, Open Graph
- any summary that repeats CV facts on another page (home page, about, footer)

Whatever is not on this list will be the one that stays wrong.

## 2. Internal consistency, within one surface

- **Role order.** Reverse-chronological throughout, unless the project deliberately
  does otherwise — and then consistently.
- **Dates.** Every range is start-before-end. Ranges do not overlap unless the roles
  genuinely were concurrent, and if they were, that should be visible. Gaps are the
  user's business, not yours to fill.
- **"Present".** At most one current role per track, and it should actually be
  current. A stale "present" is a factual error that ages in silently.
- **Derived numbers.** "N years of experience" must match the earliest start date.
  Recompute it rather than trusting the text.
- **Education.** Institution, programme and completion status stated exactly as
  approved. Never upgrade "studied" to "graduated", and never add a completion date
  that was not given.
- **Certifications.** Name, issuer and date exactly as approved. Never infer an
  issuer from a certification's name.
- **Titles.** Exactly the approved string. Never promote ("assisted" → "led",
  "developer" → "senior developer").

## 3. Cross-surface consistency

Compare each surface against the approved source, not against each other — otherwise
one wrong copy propagates.

For every fact, build a small table:

```
Fact                    web-en   pdf-en   web-me   pdf-me   JSON-LD   metadata
<role 1 title>          ✓        ✓        ✓        ✗ (old)  ✓         n/a
<date range>            ✓        ✓        ✓        ✓        ✓         n/a
```

Any `✗` is a defect. A fact present in the PDF but absent from the web page is also a
finding — usually a stale PDF nobody regenerated.

## 4. Extract the PDF's actual text

Do not assume the PDF matches the source it was generated from. Extract and compare:

```
pdftotext -layout cv.pdf - | head -100
```

If `pdftotext` (poppler-utils) is unavailable, say `pdftotext: not available` and
report the PDF as **unverified** — do not substitute the HTML source and describe it
as the PDF's content.

Check the extracted text for:

- every fact from the table above
- text that did not fit: a truncated role, a cut-off final line, a missing last page
- diacritics that survived the font embedding (`š`, `đ`, `č`, `ć`, `ž`) — a broken
  glyph shows as a missing or substituted character in the extraction
- contact details being the intended ones, and no unintended personal data
- the file's own metadata (title, author) — `pdfinfo cv.pdf`

## 5. Print layout

Render or preview the print stylesheet and check:

- nothing important is hidden by `@media print` (a nav that hides is fine; a section
  that hides is content loss)
- page breaks do not split a role's heading from its content — `break-inside: avoid`
  on entry blocks
- link URLs are visible or the links are meaningful without them
- colours and background images degrade to something readable in monochrome
- it fits the intended page count; a CV that silently becomes three pages is a defect

## 6. Metadata and structured data

- `<title>` and description state the same role and location as the CV body
- JSON-LD (`Person`, `jobTitle`, `worksFor`, `alumniOf`, `hasCredential`) contains
  **only supported facts**. Structured data is machine-read and quoted by search
  engines — an unsupported claim there is worse than in prose
- the Open Graph image, if it contains text, shows the current title

## 7. Report

```
Surfaces:     <list, and which you actually inspected>
PDF text:     extracted with pdftotext | NOT AVAILABLE — PDF unverified
Internal:     <finding per surface>
Cross-surface:<the table, with every mismatch called out>
Print:        <findings, or "not rendered">
Metadata:     <findings>
Unsupported:  <any claim with no approved source — NEEDS USER CONFIRMATION>
Stale:        <surfaces that need regenerating, and from what>
```

Do not fix a mismatch by inventing which version is right. Report the difference and
ask which the user approves — unless the approved source makes it unambiguous.
