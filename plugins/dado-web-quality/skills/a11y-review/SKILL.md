---
name: a11y-review
description: Review keyboard navigation, focus handling, skip links, accessible names, heading structure and reduced-motion behaviour, with axe where it is available. Use when auditing accessibility, after changing interactive components or animations, or before shipping a public-facing page.
---

# Accessibility review

Automated tooling finds roughly a third of accessibility defects. Run it, then do
the keyboard pass by hand — that is where the rest are.

## 1. Automated pass, if axe is available

If the project has `@axe-core/playwright`, `@axe-core/cli` or `axe-core`, run it per
route and record the violations with their impact levels.

If it is not installed: say `axe: not available` and do the manual checks below. Do
**not** add a dependency to a user's project to run this check — propose it instead.

Record: `axe on <route> -> <n> violations (<n> critical, <n> serious, <n> moderate, <n> minor)`

## 2. Keyboard navigation, by hand

Tab through each route from the top. Confirm:

- every interactive element is reachable by Tab, in the order it appears visually
- nothing is reachable that should not be (hidden menus, off-screen carousels,
  `display: none` panels that are still focusable)
- the focus indicator is **visible on every element**, including custom buttons,
  links on coloured backgrounds, and elements with `outline: none`
- Enter and Space activate buttons; Enter activates links
- Escape closes any dialog, drawer or menu
- no keyboard trap: you can always Tab back out

Check `tabindex` values above 0 — they reorder the whole page and are almost always
a defect.

## 3. Focus restoration

- opening a dialog moves focus into it; closing returns focus to the trigger
- a modal traps focus while open, and only while open
- after a client-side route change, focus moves to a sensible place (the main
  heading or the main landmark) rather than staying on the clicked link
- focus is never lost to `<body>` after an interaction

## 4. Skip link

There should be a skip link as the first focusable element:

- hidden until focused, then visible
- its target exists and is focusable (`<main id="main" tabindex="-1">`)
- activating it actually moves focus, not just the scroll position

## 5. Accessible names

Every interactive element needs a name a screen reader can announce:

```js
[...document.querySelectorAll('a, button, input, select, textarea, [role="button"]')]
  .filter(el => !(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')
                  || el.textContent.trim() || el.getAttribute('title')))
```

Common gaps: icon-only buttons, links whose only content is an image with empty
`alt`, form inputs with a visual label that is not associated via `for`/`id`.

Decorative images take `alt=""`. Meaningful images need real alt text. An image
whose alt repeats the adjacent caption is noise — mark it decorative instead.

## 6. Headings

- exactly one `<h1>` per route, and it describes that route (check the project's
  config; the default expectation is one)
- levels do not skip going down (h2 → h4 is a defect; h4 → h2 is fine)
- headings are used for structure, not for font size

```js
[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => h.tagName + ' ' + h.textContent.trim().slice(0, 60))
```

## 7. Landmarks and language

- one `<main>`, and `<header>`, `<nav>`, `<footer>` used once each at the top level
- `<html lang>` is set, and matches the language actually rendered
- a section in a different language carries its own `lang`

## 8. Reduced motion

With `prefers-reduced-motion: reduce`:

- reveal animations, parallax, auto-playing carousels and scroll-driven effects
  are disabled or reduced to a fade
- **content still appears.** The most common defect: an element that starts at
  `opacity: 0` and is revealed by an animation stays invisible when the animation is
  suppressed. Check that every reveal target is visible with motion reduced.
- no essential information is conveyed by motion alone

## 9. Colour and contrast

Report contrast failures from the automated pass. Where you check by hand, give the
measured ratio and the requirement (4.5:1 for body text, 3:1 for large text and for
UI component boundaries). Confirm no information is conveyed by colour alone.

## 10. Report

```
[keyboard|focus|skip-link|name|heading|landmark|motion|contrast]  <route>  <impact>
  Observed: <what happens>
  Repro:    <the exact key sequence or setting>
  Standard: <the specific requirement>
  Fix:      <the smallest change>
```

State clearly what was **not** tested: no screen reader was run unless one was, and
no automated tool substitutes for that. Assistive-technology behaviour on real
hardware is `requires-manual-acceptance`.
