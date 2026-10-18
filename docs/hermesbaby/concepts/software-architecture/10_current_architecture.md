# Current architecture

## Main components

- `src/hermesbaby/__main__.py` is both the Typer CLI entry point and a home
  for substantial command behavior. It currently combines command
  registration with configuration loading, build orchestration, tool
  management, and other command functionality.
- `src/hermesbaby/conf.py` is Sphinx's configuration entry point. It contains
  settings for multiple documentation features, shared calculations, and
  Sphinx `setup(app)` hooks.
- `src/hermesbaby/Kconfig` defines the application configuration. CLI
  commands load it before starting a Sphinx build.
- The CLI exports the resolved configuration as `CONFIG_*` environment
  variables for the child Sphinx process. The Sphinx configuration reads
  that snapshot; it does not load Kconfig itself.
- Sphinx extensions and related assets already live in dedicated directories
  such as `partly/`, `drawio/`, `loflot/`, and `tag-anything/`.

## Existing boundaries

The `CONFIG_*` environment snapshot is the boundary between CLI-side
configuration loading and Sphinx configuration. This keeps Kconfig loading
out of `conf.py` and allows a build's resolved settings to be passed to the
child process.

The existing extension directories are standard Sphinx extensions or assets.
HermesBaby-specific configuration around them is currently concentrated in
the top-level `conf.py`; the directories themselves are not part of this
refactoring.

The `setup(app)` hooks collected by `conf.py` provide an existing mechanism
for registering Sphinx behavior after configuration values have been
assembled.
