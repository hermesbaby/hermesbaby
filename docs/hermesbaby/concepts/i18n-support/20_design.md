---
status: accepted
owner: dominik.schmundt@vitronic.com
updated: 2026-08-26
---

# i18n support — design

## Commands

Three subcommands under `hb i18n` (`app_i18n` Typer group in
`src/hermesbaby/__main__.py`):

- `hb i18n gettext [--partly DIR] [-v]` — thin wrapper: calls the existing
  `_build_common()` (shared with `hb text`/`hb html`/`hb pdf`) with
  `builder="gettext"`. `_build_common` derives the output dir from the
  command name (`ctx.info_name`), so this lands at `out/docs/gettext`
  automatically, no new path logic needed.
- `hb i18n update-po [-l LANG]...` — runs the same extraction, then shells
  out to `sphinx-intl update -p out/docs/gettext -d <source>/<locales> -l
  <lang> [-l <lang> ...]`. Language list defaults to the Kconfig
  `I18N__LANGUAGES` (comma-separated), overridable per-invocation with
  repeatable `--language/-l`.
- `hb i18n stats` — shells out to `sphinx-intl stat -d <source>/<locales>`
  and aggregates its per-catalog `N translated, N fuzzy, N untranslated`
  output into a per-language + overall summary, printed to stdout. Always
  passes `-d` explicitly rather than `-c conf.py`, because `sphinx-intl`'s
  `-c` resolves `locale_dirs` relative to `conf.py`'s own directory —
  which for hermesbaby is inside the installed package, not the project —
  and silently reports nothing.

## Key decisions

- **`-W` (warnings-as-error) is dropped for gettext extraction.**
  `_build_common()` gained a `warn_as_error: bool = True` parameter
  (default preserves `text`/`html`/`pdf` behavior); `hb i18n gettext` and
  the extraction step inside `hb i18n update-po` both pass
  `warn_as_error=False`, since a one-off extraction shouldn't fail on
  pre-existing orphan-doc warnings that are unrelated to translation.
- **`sphinx-intl` is a runtime dependency**, not an "external tool"
  (`external_tools.json` entry). It's a normal PyPI package installed into
  the same venv as `hermesbaby`/`sphinx`, resolved via the existing
  `_resolve_tool()` helper exactly like `sphinx-build`/`sphinx-autobuild`
  already are. This is what lets `hb i18n` skip the `HERMESBABY_CONFDIR` /
  `pipx inject --include-apps` workaround that calling `sphinx-intl` by
  hand outside `hb` requires.
- **Target languages are a new, separate Kconfig setting** (`I18N__LANGUAGES`,
  see `docs/hermesbaby/decisions/i18n-languages-as-kconfig-string.md`),
  distinct from the existing
  `DOC__LANGUAGE` single choice — one selects what a given build renders
  as, the other is the set of catalogs to keep up to date. A project may
  maintain German and English catalogs while still building only English
  by default.
- **No `.mo`-compiling command.** Sphinx compiles `.po` → `.mo`
  automatically at build time (`gettext_auto_build` defaults to `True`).
- **The locales directory is configurable** (`I18N__DIR_LOCALES`, relative
  to the Source Directory), defaulting to `_locales` rather than bare
  `locales` — a real project's `docs/` tree is mostly content-chapter
  folders (`docs/AI-Strategy/`, `docs/CSEP/`, ...), and an unprefixed
  `locales/` sitting alongside them reads like just another chapter.
  Underscore-prefixing matches the existing `_figures`/`_attachments`/
  `_listings`/`_unused` convention for infrastructure folders, all of
  which are already excluded from Sphinx's document discovery via
  `exclude_patterns` in `conf.py` — `I18N__DIR_LOCALES` is now excluded
  the same way.

## Files touched

- `src/hermesbaby/__main__.py` — three `app_i18n` commands, `warn_as_error`
  param on `_build_common`.
- `src/hermesbaby/Kconfig` — new `menu "i18n"` / `I18N__LANGUAGES` /
  `I18N__DIR_LOCALES`.
- `src/hermesbaby/conf.py` — `locale_dirs` reads `I18N__DIR_LOCALES`
  instead of a hardcoded `'locales/'`; that directory is added to
  `exclude_patterns` alongside the other underscore-prefixed infra dirs.
- `pyproject.toml` — `sphinx-intl` runtime dependency.
- `src/hermesbaby/templates/{hello,zero}/.../.gitignore` — ignore
  `docs/_locales/**/*.mo` (commit `.po`, not compiled `.mo`).
- `tests/e2e/test-i18n.bats` — new.
