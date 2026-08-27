---
name: deploy-preview-check
description: Verify a deploy preview or production deployment against a specific commit, comparing the served build to a clean local build and running a smoke pass. Use when a hosting provider produces a preview URL, before approving a deployment, and after one has gone out.
---

# Deploy preview and production verification

The question is never "did the deploy succeed". It is "is the thing serving at this
URL built from the commit I reviewed, and does it work".

## 1. Bind the URL to a commit

```
Preview/production URL: <url>
Expected commit:        <full 40-char SHA>
Reported commit:        <what the host says it deployed>
Match:                  yes | no | host does not report it
```

Where the host exposes a deployed-commit field, read it. Netlify, Vercel and similar
report the commit ref per deploy. If the host does not expose it, say so — then the
only remaining evidence is the artifact comparison in step 2, and you should say
that too.

If the commit does not match, stop. Everything you check afterwards describes a
different build.

## 2. Compare the served build to a clean local build

Build locally from that exact commit with a clean tree, then compare digests:

```
git status --porcelain=v1        # must be empty
git rev-parse HEAD               # must be the expected SHA
<the project's clean + build commands>
sha256sum <dist>/<asset>
curl -sS <url>/<same asset path> | sha256sum
```

- **Equal digests** → the served bytes are your bytes. This is the strongest proof.
- **Different digests** → name the cause before calling it a problem: embedded build
  timestamp, embedded commit SHA, minifier version, host re-compression. Compare the
  decoded body, not the compressed transfer.
- **Could not fetch** → `not-verified`, never "matches".

For an SPA, compare the fingerprinted asset names referenced by the served
`index.html` against the ones your build produced. A mismatch there means the served
HTML and the served assets came from different builds.

## 3. Smoke pass on the deployed site

Run against the real URL, not a local dev server:

- the home route loads, status 200, no console errors, no failed requests
- the specific behaviour the change touched works
- one route that already worked still works
- a hard load of a nested route returns the right status (not a 200 for a 404)
- the `og:image` URL loads
- security and caching headers are the ones intended (`/dado-web-quality:headers-and-hosting`)
- at least one mobile viewport renders without horizontal overflow

Record each as observed or `not-checked`.

## 4. Preview is not production

A preview deploy can differ from production in ways that matter:

- environment variables and API endpoints
- `robots.txt` (previews are usually `Disallow: /` — confirm production is not)
- redirect and header rules scoped to the production branch
- CDN caching behaviour and edge configuration
- the domain, which affects canonicals, CORS, cookies and CSP

State which you verified on the preview and which remain unverified for production.
A green preview is evidence about the preview.

## 5. After a production deployment

Re-run the smoke pass against production. Additionally:

- confirm the deployed ref again — a queued deploy may have superseded yours
- check that previously cached HTML does not reference deleted asset hashes
- have the rollback target written down before you look (see
  `/dado-release-safety:deploy-gate` if that plugin is installed)

## 6. Report

```
URL:            <url>   (preview | production)
Expected SHA:   <full SHA>
Reported SHA:   <full SHA | not reported by host>
Asset compare:  <asset> local=<digest> served=<digest> — match | differ (<cause>) | not fetched
Smoke:          <check> — pass | fail | not-checked
Headers:        <observed> | not fetched
Differs from production: <env, robots, redirects, domain — what you could not verify>
Verdict:        <what this proves, and what it does not>
```

This skill verifies. It does not deploy, promote, or approve a deployment.
