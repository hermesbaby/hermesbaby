---
status: accepted
decided: 2026-08-27
---

# Default the locales directory to an underscore-prefixed name

## Context and Problem Statement

`hb i18n update-po`/`stats` need a directory to store `.po`/`.mo`
translation catalogs in, relative to the Source Directory. The original
implementation hardcoded `locales/`, matching Sphinx's own convention
(`locale_dirs`). In a real project's `docs/` tree, though, that directory
sits as a sibling of content-chapter folders (`docs/AI-Strategy/`,
`docs/CSEP/`, `docs/notes/`, ...) with no visual distinction from them —
it reads as just another chapter rather than infrastructure.

## Considered Options

- Keep the bare `locales` default, unconfigurable.
- Keep `locales` as the default but make it configurable.
- Default to an underscore-prefixed name (`_locales`) and make it
  configurable.

## Decision Outcome

Chosen: configurable, defaulting to `_locales`. `conf.py` already has an
established convention for infrastructure/non-chapter folders —
`_figures`, `_attachments`, `_listings`, `_unused` — all underscore-
prefixed and excluded from Sphinx's document discovery via
`exclude_patterns`. `_locales` joins that convention rather than
inventing a new one, and sorts/visually groups next to the others in a
file listing. Making it configurable (`I18N__DIR_LOCALES` in
`src/hermesbaby/Kconfig`) rather than hardcoding the new name accommodates
projects with an existing `locales/` (or other) directory already in use,
without forcing a rename.

## Consequences

- Good: distinguishable from content chapters by convention, consistent
  with `_figures`/`_attachments`/`_listings`/`_unused`.
- Good: `I18N__DIR_LOCALES` is now excluded from `exclude_patterns` the
  same way the other underscore-prefixed dirs are, so it can never
  accidentally be picked up as document source.
- Bad: renames the default relative to the originally-shipped
  hardcoded `locales/` — a project created against an earlier build of
  this feature (before it landed in a release) would need to either move
  its catalogs or set `I18N__DIR_LOCALES="locales"` explicitly. No
  released version shipped the old default, so no real migration exists.
