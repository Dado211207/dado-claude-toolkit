---
name: seo-and-metadata
description: Check per-route titles and descriptions, canonical URLs, hreflang, Open Graph and Twitter cards, sitemap, robots.txt and structured data, and confirm metadata matches the visible page. Use after changing page metadata, adding routes or languages, or before a site goes live.
---

# Metadata and SEO

The failure that matters most here is metadata that contradicts the page. Check
against what the page actually says, not against what the metadata claims.

## 1. Per-route basics

For every route, on a **hard load** (metadata injected only by client-side script is
invisible to most crawlers — note when that is the case):

| Element | Requirement |
| --- | --- |
| `<title>` | Unique per route, describes that route, not truncated mid-word |
| `<meta name="description">` | Unique per route, describes that route |
| `<html lang>` | Present, matches the language rendered |
| `<h1>` | Present, one per route, consistent with the title |
| `<meta name="viewport">` | `width=device-width, initial-scale=1` |

The check that finds real bugs: **does the title match the page?** A route whose
title says one city and whose content says another is a copy regression, not a
metadata style issue. Same for job titles, organisation names and dates.

## 2. Canonical URLs

- exactly one `<link rel="canonical">` per route
- absolute URL, correct scheme and host, no trailing-slash inconsistency with what
  the host actually serves
- self-referencing on the canonical version of the page
- no canonical pointing at the home page from every route — a common copy-paste bug
  that de-indexes the whole site

## 3. hreflang, for multilingual sites

For each language version of a page:

- `<link rel="alternate" hreflang="<lang>" href="<absolute url>">` for **every**
  language, including the page's own
- an `x-default` entry
- **reciprocity**: if EN points at ME, ME must point back at EN. One-way hreflang is
  ignored
- language codes are valid and match `<html lang>`

Use the project's configured languages. For an EN/ME site, both `en` and `me` sets
must exist on both pages.

## 4. Open Graph and Twitter

| Property | Note |
| --- | --- |
| `og:title`, `og:description` | Should match, or deliberately differ from, the page title/description — not contradict it |
| `og:url` | Absolute, matches canonical |
| `og:type` | `website` or `article` as appropriate |
| `og:image` | Absolute URL, actually loads (fetch it), at least 1200×630 |
| `og:locale`, `og:locale:alternate` | Set for multilingual sites |
| `twitter:card` | `summary_large_image` when there is an image |

Fetch the `og:image` URL and confirm it returns 200 with an image content type. A
broken preview image is the most common and most visible metadata defect.

## 5. Sitemap and robots

- `robots.txt` exists, is served as `text/plain`, and does not block routes that
  should be indexed. Confirm a production build does not ship a `Disallow: /` left
  over from a staging config
- `sitemap.xml` exists, is valid XML, lists the canonical URL of every public route,
  and lists no 404s or redirects
- `robots.txt` references the sitemap
- every URL in the sitemap uses the same host and scheme as the canonicals

Fetch a sample of sitemap URLs and check their status codes.

## 6. Structured data

If the site uses JSON-LD:

- it parses as JSON
- `@context` and `@type` are set
- every claim in it is **true and supported by the page**. Structured data that
  states a qualification, an award, a rating, an employer or a date the page does
  not support is a fabricated claim, and is worse than having none
- it does not contradict the visible content

Do not add structured data claims that the user has not confirmed.

## 7. Report

```
[title|description|canonical|hreflang|og|robots|sitemap|structured-data|contradiction]  <route>
  Observed: <the actual value>
  Expected: <the requirement, or the visible page content it contradicts>
  Fix:      <the change>
```

Say whether metadata was read from a hard load or after client-side hydration, and
which routes you sampled versus checked exhaustively.
