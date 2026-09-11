---
status: open
owner: dominik.schmundt@vitronic.com
updated: 2026-08-26
---

# i18n support: two install paths not yet verified/fixed

Follow-up from adding `sphinx-intl` as a runtime dependency for
`hb i18n` (see `docs/hermesbaby/concepts/i18n-support/`). The primary
install path — `pipx install hermesbaby` — was verified end-to-end: a
real `pipx install --force .` from this branch puts `sphinx-intl.exe`
in the same venv `Scripts/` dir as `hb.exe`, and `hb i18n update-po`
resolves it via the existing `_resolve_tool()` helper with `sphinx-intl`
absent from global PATH. Two other paths are known gaps, not yet fixed:

## 1. `poetry.lock` out of sync

`pyproject.toml` now lists `sphinx-intl`, but `poetry.lock` was not
regenerated (poetry wasn't available in the environment this was built
in). Doesn't affect `pip`/`uv tool`/`pipx install` — those build from
`pyproject.toml`/wheel metadata directly, not the lock file — but breaks
the documented dev workflow (`poetry install --with dev` in `README.md`
and `build-windows.cmd`).

**Fix:** run `poetry lock` (or `poetry lock --no-update` to avoid
bumping unrelated pins) and commit the regenerated `poetry.lock`.

## 2. PyInstaller frozen binary missing `sphinx-intl`

`hermesbaby.spec`'s `entry_points` list controls which console-script
executables get bundled into the `dist/hb.exe` / `hermesbaby-windows-x64.zip`
binary distribution (`build-windows.cmd`):

```python
entry_points = ["sphinx-build", "sphinx-apidoc", "sphinx-autobuild", "guiconfig", "menuconfig"]
```

`sphinx-intl` isn't in it, so a frozen binary build currently ships
without i18n support — `hb i18n update-po`/`stats` would fail to
resolve the `sphinx-intl` executable in that distribution.

**Fix:** add `"sphinx-intl"` to that list.
