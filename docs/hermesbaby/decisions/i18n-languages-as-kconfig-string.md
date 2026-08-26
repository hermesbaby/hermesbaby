---
status: accepted
decided: 2026-08-26
---

# Represent i18n target languages as a comma-separated Kconfig string

## Context and Problem Statement

`hb i18n update-po` / `hb i18n stats` need to know which languages to
maintain `.po` translation catalogs for. This is a genuine list (a project
may translate into several languages at once), but Kconfig — the config
system `hermesbaby` uses throughout (`src/hermesbaby/Kconfig`) — has no
native multi-select construct; every existing selection in the file
(`DOC__LANGUAGE`, `DOC__CONFIDENTIALITY_LEVEL`, `SCM__OWNER_KIND`) is a
single `choice`/`endchoice`, which picks exactly one option.

## Considered Options

- Reuse the existing `DOC__LANGUAGE` single choice as the language to
  maintain catalogs for.
- Model each supported language as its own `bool` config (`I18N__LANG_EN`,
  `I18N__LANG_DE`, ...), toggled independently.
- A single free-form comma-separated `string` config
  (`I18N__LANGUAGES`, e.g. `"en,de"`).

## Decision Outcome

Chosen: a comma-separated `string` config. `DOC__LANGUAGE` answers a
different question (what a given build renders as) than "which catalogs
do we keep up to date" — conflating them would make it impossible to
maintain a German catalog while still building English by default, which
is the common case per the requirements
(`docs/hermesbaby/concepts/i18n-support/10_requirements.md`: translation
is optional per page, catalogs cover the whole tree regardless of source
language). Per-language `bool` configs
would need editing `Kconfig` itself to add a new language, whereas a
string is open-ended and needs no code change to support an arbitrary
language code.

## Consequences

- Good: adding a new target language is a one-line `.hermesbaby` edit
  (`CONFIG_I18N__LANGUAGES="en,de,fr"`), no `Kconfig` change needed.
- Good: `hb i18n update-po -l <lang>` can still override per-invocation
  without touching the persisted config.
- Bad: no validation of language codes at the Kconfig level (a typo like
  `"en,gr"` is only caught when `sphinx-intl`/Sphinx rejects it later) —
  acceptable since the existing `DOC__LANGUAGE` choice already documents
  the two "real" language options (English/German) as the primary,
  validated path; `I18N__LANGUAGES` is deliberately looser since it's a
  maintenance list, not a per-build selection.
