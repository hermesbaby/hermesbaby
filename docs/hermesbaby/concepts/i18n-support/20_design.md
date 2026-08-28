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
- `hb html`/`hb html-live`/`hb pdf`/`hb pdf-live` gained `--language/-l`
  to preview a build in a specific language for one invocation — see
  "Language override for html/pdf builds" below.

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

## Language override for html/pdf builds

`hb html`/`hb html-live`/`hb pdf`/`hb pdf-live` gained `--language/-l` to
build in a given language for one invocation, without editing
`.hermesbaby` — needed to preview/test a translated build.

- Implemented via a `HERMESBABY_LANGUAGE` environment variable (same
  pattern as the existing `HERMESBABY_CWD`/`HERMESBABY_PART_DIR`),
  set by `_set_env()` and read by `conf.py`:
  `language = os.environ.get("HERMESBABY_LANGUAGE") or kconfig.syms["DOC__LANGUAGE"].str_value`.
  A plain Sphinx `-D language=...` override was considered instead, but
  Sphinx only applies `-D` overrides *after* `conf.py` finishes running,
  so `conf.py`'s own module-level code (see next point) can never observe
  it — an environment variable is visible immediately, at `conf.py`
  exec time.
- The LaTeX babel-selection block (which picks `ngerman`/`english` for
  hyphenation) used to re-derive its own answer from the raw
  `DOC_LANGUAGE_GERMAN`/`DOC_LANGUAGE_ENGLISH` Kconfig choice symbols,
  bypassing the `language` value entirely. That would have silently
  ignored the override for PDF builds (correct translated content, wrong
  hyphenation language). Fixed by deriving `_is_german`/`_is_english`
  from the resolved `language` variable instead — one source of truth,
  correct with or without an override.
- **Known limitation:** `DOC__CONFIDENTIALITY_LEVEL_LABEL`/
  `DOC__CONFIDENTIALITY_LEVEL` are Kconfig-conditional defaults keyed off
  the *persisted* `DOC_LANGUAGE_ENGLISH`/`DOC_LANGUAGE_GERMAN` choice, not
  off `HERMESBABY_LANGUAGE` — an override only reaches `conf.py`'s own
  `language` variable, not Kconfig's internal choice state. A `--language
  de` build still shows the English confidentiality label. Not fixed here:
  doing so would mean mutating kconfig's own symbol values at runtime, and
  the override is meant for previewing translated content/layout, not for
  re-deriving every Kconfig default that happens to branch on language.

## Files touched

- `src/hermesbaby/__main__.py` — three `app_i18n` commands, `warn_as_error`
  param on `_build_common`; `--language/-l` option on `html`/`html-live`/
  `pdf`/`pdf-live`, `language` param threaded through `_set_env`/
  `_build_common`.
- `src/hermesbaby/Kconfig` — new `menu "i18n"` / `I18N__LANGUAGES` /
  `I18N__DIR_LOCALES`.
- `src/hermesbaby/conf.py` — `locale_dirs` reads `I18N__DIR_LOCALES`
  instead of a hardcoded `'locales/'`; that directory is added to
  `exclude_patterns` alongside the other underscore-prefixed infra dirs.
- `pyproject.toml` — `sphinx-intl` runtime dependency.
- `src/hermesbaby/templates/{hello,zero}/.../.gitignore` — ignore
  `docs/_locales/**/*.mo` (commit `.po`, not compiled `.mo`).
- `tests/e2e/test-i18n.bats` — new.
