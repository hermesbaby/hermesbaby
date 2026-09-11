---
status: accepted
owner: dominik.schmundt@vitronic.com
updated: 2026-08-26
---

# i18n support — requirements

## What & why

`hermesbaby` already wires Sphinx for translation (`language`,
`locale_dirs`, `gettext_compact` in `conf.py`), but nothing drives the
extract → merge → translate → build workflow. Authors currently have to
hand-roll `sphinx-build -b gettext` + `sphinx-intl` invocations outside
`hb`, including a workaround to locate hermesbaby's bundled `conf.py`
(`HERMESBABY_CONFDIR`) since it isn't installed alongside `docs/`.

Goal: expose that workflow as first-class `hb i18n` subcommands so a
project can extract translatable strings, maintain per-language `.po`
catalogs, and check translation coverage without leaving `hb`.

## Acceptance criteria

- `hb i18n gettext` extracts `.pot` catalogs from the current doc source
  tree (one `.pot` per source document, mirroring the source layout, per
  `gettext_compact = False`).
- `hb i18n update-po` extracts and then creates/refreshes `.po` catalogs
  under `<source>/<I18N__DIR_LOCALES>/<lang>/LC_MESSAGES/` (default
  `_locales`, itself configurable) for a configurable set of languages,
  without discarding existing translations (merge semantics).
- `hb i18n stats` reports raw per-catalog translated / fuzzy / untranslated
  counts, passing through `sphinx-intl stat`'s own output format
  unmodified.
- `hb i18n stats-summary` reports the same counts aggregated per-language
  and overall.
- Building with an existing `.po` catalog for the active `DOC__LANGUAGE`
  (e.g. `hb html`) picks up translations automatically — this already
  works via Sphinx's `gettext_auto_build` and required no new code.
- `hb html`/`hb html-live`/`hb pdf`/`hb pdf-live` accept `--language/-l`
  to build/preview a specific language for one invocation, without
  editing `.hermesbaby` — needed to test each translated version without
  reconfiguring the project per language.
- Works on Windows and Linux (no reliance on `awk`/bash-only tooling).

## Non-goals

- Compiling `.po` → `.mo` explicitly (Sphinx already does this at build
  time via `gettext_auto_build`).
- Per-page source-language tagging / hyphenation correctness for
  untranslated fallback content (tracked as a possible follow-up, not
  needed for the base workflow — translation is optional per page and
  Sphinx already falls back to source text silently).
- A managed list of allowed language codes / validation — `I18N__LANGUAGES`
  is a free-form comma-separated string.

## Reference

Validated by hand in a separate project before being built into `hb`; see
`po-file-update.sh` / `po-stats.sh` and the write-up that documents the
gotchas this feature designs around (bundled `conf.py` location, `-W`
breaking a one-off extraction on pre-existing warnings, `sphinx-intl stat
-c` silently finding nothing).
