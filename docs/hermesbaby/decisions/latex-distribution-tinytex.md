---
status: accepted
decided: 2026-10-18
---

# Install an hb-managed TinyTeX for PDF builds

## Context and Problem Statement

`hb pdf` needs LuaLaTeX, latexmk and a set of LaTeX packages and fonts.
Until now only CI got them installed (`hb ci install-tools`, apt, Debian
only). On Windows and macOS users had to pick, install and configure a
distribution themselves. MiKTeX in particular prompts for packages during
the build unless configured otherwise. PDFs also looked different per
platform: Segoe UI on Windows, DejaVu Sans elsewhere, while macOS ships
no DejaVu fonts at all.

## Considered Options

- Native package managers per OS (apt, scoop/winget MiKTeX, brew MacTeX).
- TeX Live via `install-tl` and a profile.
- TinyTeX, a portable TeX Live with prebuilt bundles for all three OSes.
- MiKTeX with on-the-fly installation enabled.
- Tectonic.

## Decision Outcome

Chosen: TinyTeX, managed by hermesbaby (`hb tools latex install|check|doctor|update|uninstall|path`).

- Installed per user without admin rights, into `%LOCALAPPDATA%\hermesbaby\TinyTeX`,
  `~/Library/hermesbaby/TinyTeX` or `~/.local/share/hermesbaby/TinyTeX`
  (`HERMESBABY_TINYTEX_DIR` overrides).
- Never added to the global PATH. `hb pdf` puts it first on the build's
  PATH. Without it, `hb pdf` falls back to a TeX distribution on PATH, which
  is how CI keeps using apt's TeX Live.
- Headless: TeX Live never installs packages on the fly, so builds can't
  prompt. All packages come from `src/hermesbaby/tinytex/packages.txt` at
  install time, and the luaotfload font database is built at install time too.
  `TEXMFHOME`/`TEXMFVAR`/`TEXMFCONFIG` point into the installation, so a
  user's own LaTeX setup neither interferes nor gets modified.
- One font family on every platform: DejaVu Sans / DejaVu Sans Mono
  (TeX Live package `dejavu`; Debian `fonts-dejavu` in CI), referenced by
  file name.

Tectonic was rejected because it does not support LuaLaTeX and downloads
packages during the build. MiKTeX auto-install was rejected because it needs
the network during builds and is not reproducible.

## Consequences

- Good: one command, the same procedure on all three OSes, no admin rights.
- Good: PDFs look the same on every platform.
- Bad: the package list has to be maintained by hand, since tlmgr doesn't
  resolve dependencies between ordinary packages. `hb tools latex doctor --fix`
  finds the providing package for a missing file.
- Bad: after a new yearly TeX Live release, `tlmgr` of an old install can't
  install packages from the current repository. `hb tools latex install --force`
  replaces the installation.
- Bad: TinyTeX has no prebuilt bundle for Linux on ARM; `install` stops
  with an error there.
- Changed look: Windows PDFs switch from Segoe UI to DejaVu Sans, and code
  blocks everywhere switch from FreeMono to DejaVu Sans Mono.
