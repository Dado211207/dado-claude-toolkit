# dado-ui-design

Local, searchable UI/UX design intelligence for web, mobile and desktop work. It
complements `dado-web-quality`: this plugin helps choose and implement a coherent
visual direction; `dado-web-quality` verifies observable behaviour, accessibility,
responsive layout and production delivery.

- **Version:** 0.1.0
- **Marketplace:** `dado-tools`
- **Install:** `/plugin install dado-ui-design@dado-tools`
- **Skill:** `/dado-ui-design:ui-ux-pro-max`
- **Runtime:** Python 3 standard library only; no network request and no package
  installation

## What it provides

The `ui-ux-pro-max` skill contains a local design catalogue and search tool covering
product patterns, styles, palettes, typography, accessibility and UX guidance,
icons, animation patterns, charts, and stack-specific implementation guidance.
Supported targets include ordinary HTML/CSS, React and other web stacks, as well as
Windows UI stacks such as WPF and WinUI.

Typical use:

```text
/dado-ui-design:ui-ux-pro-max
```

The skill then runs its own local search script when a design decision needs evidence.
For example, it can generate a proposed design system for a desktop assistant or
look up focused guidance for keyboard focus, responsive navigation or motion.

## Safety and trust

- The catalogue is a reviewed, pinned snapshot of the MIT-licensed
  `nextlevelbuilder/ui-ux-pro-max-skill` project. Exact provenance is recorded in
  [THIRD_PARTY.md](THIRD_PARTY.md), and its license is included in
  [THIRD_PARTY_LICENSE.txt](THIRD_PARTY_LICENSE.txt).
- Only the runtime skill, data, references and standard-library Python search files
  are vendored. Upstream development tests and maintenance utilities are not shipped.
- The runtime makes no network request and launches no external process. Search input
  stays local.
- Search output is design guidance, not authority. It cannot override the user,
  repository rules, factual content, accessibility requirements or release gates.
- Persistence is opt-in. The skill requires an explicit project output directory and
  will not overwrite an existing design system unless the user explicitly authorizes
  `--force`.

## Updating the snapshot

Do not copy from an unpinned default branch. Record the new upstream commit, review
the complete diff and license, re-run upstream tests and this repository's validation,
then update `THIRD_PARTY.md`. A changed provenance commit without a corresponding
review must fail validation.

## Uninstall

```text
/plugin uninstall dado-ui-design@dado-tools
```

Any design-system files explicitly persisted into a project belong to that project
and are not removed automatically.
