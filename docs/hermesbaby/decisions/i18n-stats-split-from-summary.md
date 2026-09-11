---
status: accepted
decided: 2026-08-28
---

# Split `hb i18n stats` into raw pass-through and `stats-summary`

## Context and Problem Statement

`hb i18n stats` shelled out to `sphinx-intl stat` and appended an
aggregated per-language/overall summary after the raw per-catalog lines.
Any script or tool that parses `sphinx-intl stat`'s well-known output
format (one `N translated, N fuzzy, N untranslated` line per catalog)
would break on the extra summary lines appended after it, since that
tool has no way to know where sphinx-intl's own output ends.

## Considered Options

- Keep `stats` as-is (raw output + summary combined).
- Add a flag (e.g. `--no-summary`) to suppress the summary on request.
- Split into two commands: `stats` (raw pass-through) and
  `stats-summary` (aggregated only).

## Decision Outcome

Chosen: split into two commands. `hb i18n stats` now prints
`sphinx-intl stat`'s output unmodified (aside from the command-echo line
every `hb` subcommand prints, which is not part of sphinx-intl's own
output format and precedes it). `hb i18n stats-summary` runs the same
underlying call (factored into `_i18n_run_sphinx_intl_stat()`) and prints
only the aggregated per-language/overall counts, no raw per-catalog
lines.

A flag was rejected because it still leaves `stats`'s default behavior
(summary included) as the format-breaking one — a tool would have to
know to pass `--no-summary`, whereas a plain `stats` should be safe to
parse by default.

## Consequences

- Good: `hb i18n stats` is safe for tools/scripts that depend on
  `sphinx-intl stat`'s known output format.
- Good: the aggregated view is still one command away
  (`hb i18n stats-summary`) for humans checking coverage at a glance.
- Bad: `hb i18n` now has two stats-flavored commands instead of one;
  mitigated by each command's `--help` text cross-referencing the other.
