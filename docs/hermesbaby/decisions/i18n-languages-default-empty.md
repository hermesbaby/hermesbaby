---
status: accepted
decided: 2026-09-01
---

# Default I18N__LANGUAGES to an empty string

## Context and Problem Statement

`I18N__LANGUAGES` (see `docs/hermesbaby/decisions/i18n-languages-as-kconfig-string.md`)
defaulted to `"en,de"`, so a project with no `.hermesbaby` at all — or one that
simply never set the value — silently maintained English and German
catalogs. That default only affects `hb i18n update-po`/`hb i18n stats`;
`hb html`/`hb pdf` never read `I18N__LANGUAGES`, they build whatever
`DOC__LANGUAGE` (or a `--language` override) says regardless. A CI pipeline
that wants a simple "build the doc as configured" step, and only build/
maintain extra languages when a project has actually set them up, was
forced to either accept the `en,de` default's catalog maintenance or
override it every time.

## Considered Options

- Keep `"en,de"` as the default.
- Default to `""` (empty), requiring a project to opt in.

## Decision Outcome

Chosen: default to `""`. i18n catalog maintenance becomes opt-in per
project, matching the general shape of a "simplified CI pipeline" where the
document build itself is unaffected either way (it never consulted this
setting) and only `update-po`/`stats` change behavior.

## Consequences

- Good: a project that hasn't set up i18n gets no unrequested `en`/`de`
  catalog scaffolding from `update-po`.
- Good: CI can treat "is `I18N__LANGUAGES` non-empty" as the signal for
  whether to run catalog-maintenance/multi-language steps at all.
- Bad: `hb i18n update-po` with no `.hermesbaby` and no `-l` now exits 1
  ("No languages given...") instead of defaulting to `en,de` — the
  previous no-config quick-start path requires an explicit `-l` or a
  `.hermesbaby` with `CONFIG_I18N__LANGUAGES` set (e.g. via
  `hb configure`).
