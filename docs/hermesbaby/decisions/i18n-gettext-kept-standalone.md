---
status: accepted
decided: 2026-08-27
---

# Keep `hb i18n gettext` as a standalone command

## Context and Problem Statement

`hb i18n update-po` already performs message extraction internally (the
same `sphinx-build -b gettext` call `hb i18n gettext` makes) before
running `sphinx-intl update`. That makes the visible three-command
surface (`gettext`, `update-po`, `stats`) look like a three-step workflow
you must run in order, when in fact `update-po` alone is sufficient for
the normal case — `gettext` is never a prerequisite. Given that
redundancy, is a standalone `gettext` command still worth keeping?

## Considered Options

- Remove `gettext`; keep only `update-po` (extract + merge) and `stats`.
- Keep all three as-is, undocumented relationship.
- Keep all three, but document in `--help` that `update-po` already
  extracts internally and `gettext` is a standalone diagnostic step.

## Decision Outcome

Chosen: keep `gettext`, with the relationship documented in each
command's `--help` text (see `src/hermesbaby/__main__.py`,
`i18n_gettext`/`i18n_update_po` docstrings). Reasons:

- **Side-effect-free diagnostics.** `gettext` needs nothing beyond a
  working Sphinx source tree — no `sphinx-intl`, no `I18N__LANGUAGES`,
  no writes under `<source>/<I18N__DIR_LOCALES>`. It answers "does
  extraction even succeed, any orphan-doc warnings?" without touching
  translator-owned `.po` catalogs. Folding it into `update-po` would mean
  every such check also runs the merge step and modifies the catalogs.
- **Naming symmetry.** `text`/`html`/`pdf`/`gettext` each map 1:1 onto a
  Sphinx builder name (see `_build_common` in `__main__.py`, shared by
  all four). Removing `gettext` breaks that pattern as the only builder
  without a matching command.
- **External translation platforms.** A project syncing catalogs through
  Weblate/Transifex-style tooling instead of local `sphinx-intl` may want
  fresh `.pot` templates published without ever invoking `sphinx-intl`.
- **Cost of keeping it is low.** Extraction is fast and idempotent;
  running it twice in a row (once via `gettext`, once via `update-po`)
  is harmless, so the redundancy is a documentation problem, not a
  correctness or performance one.

## Consequences

- Good: `gettext` remains available for fast, no-side-effect extraction
  checks and for non-`sphinx-intl` translation workflows.
- Good: `text`/`html`/`pdf`/`gettext` stay symmetric as one command per
  Sphinx builder.
- Bad: the three-command surface still reads as a linear workflow at a
  glance; mitigated, not eliminated, by spelling out the relationship in
  `--help` for `gettext` and `update-po`.
