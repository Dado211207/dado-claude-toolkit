---
name: headers-and-hosting
description: Verify security and caching headers as actually served, and validate host redirect and header rules including Netlify _redirects, _headers and netlify.toml. Use after changing hosting configuration, before a site goes live, or when a redirect, cache or CSP problem is reported.
---

# Headers and hosting configuration

Read the config to know the intent; fetch the URL to know the reality. They differ
more often than not.

## 1. Observe what is actually served

```
curl -sSI <origin>/                       # HTML document
curl -sSI <origin>/<hashed-asset>         # a fingerprinted JS/CSS file
curl -sSI <origin>/<image>
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" <origin>/<path>
```

If the origin is unreachable from this session, say `not-run: no network egress to
<origin>` and review the configuration files only — clearly labelled as intent, not
as observed behaviour.

## 2. Security headers

| Header | What to check |
| --- | --- |
| `content-security-policy` | Present; no `unsafe-eval`; `unsafe-inline` only with a stated reason; `default-src` not `*` |
| `x-content-type-options` | `nosniff` |
| `referrer-policy` | Set, e.g. `strict-origin-when-cross-origin` |
| `strict-transport-security` | Present on HTTPS, with a real `max-age` |
| `x-frame-options` or CSP `frame-ancestors` | Set unless embedding is intended |
| `permissions-policy` | Denies features the site does not use (camera, microphone, geolocation) |
| `x-powered-by`, `server` | Should not advertise the stack |

A CSP is only real if the page works under it. Load the site and check the console
for CSP violation reports — a policy that blocks the site's own scripts is usually
followed by someone disabling it entirely.

## 3. Caching headers

| Resource | Expected |
| --- | --- |
| Fingerprinted assets (`app.a1b2c3.js`) | `cache-control: public, max-age=31536000, immutable` |
| HTML documents | `no-cache` or a short max-age with revalidation |
| `robots.txt`, `sitemap.xml` | Short max-age |
| Images without a content hash | Moderate max-age |

The failure that hurts: HTML cached long. Users then keep an old document that
references deleted asset hashes, and the site breaks after a deploy for exactly the
people who visited before it.

## 4. Netlify redirect and header rules

Rules can live in `public/_redirects`, `public/_headers` and `netlify.toml`. Where a
path is matched in more than one place, `_redirects` and `_headers` are processed
alongside `netlify.toml` — so check both rather than assuming one wins, and confirm
the outcome by fetching the URL.

`_redirects` — one rule per line, `from  to  [status]`:

- **Order matters**: the first match wins. A catch-all placed above specific rules
  silently disables them. Read the file top to bottom and find the first rule that
  matches each test path.
- The SPA fallback belongs **last**: `/*  /index.html  200`
- `200` is a rewrite (URL unchanged), `301`/`302` are redirects (URL changes). Using
  `200` where a redirect was intended creates duplicate content at two URLs; using a
  redirect for the SPA fallback breaks deep links.
- A rule with a `404` status serves the custom 404 with the right code — check
  whether the project wants the SPA fallback or a real 404 for unknown paths.
- Splats (`/old/*  /new/:splat  301`) and placeholders (`/:id`) must be tested with
  a real path, not assumed.

`_headers` — path pattern, then indented `Key: value` lines:

- indentation is significant; a non-indented header line is silently ignored
- more specific paths do not automatically override broader ones the way CSS does —
  verify by fetching

Verify each rule you care about:

```
curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" <origin>/<old-path>
curl -sSI <origin>/<path> | grep -i '<header-name>'
```

## 5. Redirect hygiene

- no redirect chains (A → B → C); point A at C
- no redirect loops
- HTTP redirects to HTTPS; the bare domain and `www` resolve to one canonical host
- redirects preserve the path and query string where they should
- the canonical URL in the page metadata matches the URL the host actually settles on

## 6. Report

```
[security-header|cache|redirect|rewrite|404|canonical-host]  <path>
  Configured: <the rule, and which file it came from>
  Served:     <the observed status/header, or "not fetched">
  Expected:   <the requirement>
  Fix:        <the change, in the file that actually governs this path>
```

Separate "the config says" from "the server did". Only the second is evidence.
