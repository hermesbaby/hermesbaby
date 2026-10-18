# Feature inventory and migration order

This is an initial inventory of user-visible functionality and the current
implementation boundaries. It is based on the existing CLI registrations,
Sphinx configuration, package directories, and tests. The order below is a
proposal for discussion, not a commitment to move code before the target
architecture is agreed.

## CLI functionality

| Functionality | Current implementation | Sphinx/config relationship | Existing verification | Initial assessment |
| --- | --- | --- | --- | --- |
| `hb new` | CLI command in `src/hermesbaby/__main__.py`; templates under `src/hermesbaby/templates/`; uses Cookiecutter. | No Sphinx configuration interface. It currently calls `_set_env()` and `_load_config()`, but all built-in `cookiecutter.json` files provide only `directory`; `CONFIG_*` template references are for later Sphinx rendering. It still needs packaged-template resource lookup. | `tests/e2e/test-new.bats`, `tests/e2e/test-env-precedence.bats`, and template-related tests. | Best first substantial feature candidate. Keep behavior stable, determine whether the environment/config setup can be removed, and make template resource lookup an explicit dependency. |
| `hb ci config-to-env` | CLI adapter in `__main__.py`; parsing and formatting already live in `hermesbaby.ci.parse_config`. | No Kconfig loading or Sphinx configuration interface. | No command-specific test found in the current test tree. | Smallest technical extraction candidate; add a focused CLI test as part of the move. |
| `hb vscode check/install/uninstall` | CLI commands and helper functions in `__main__.py`; recommendations and VSIX files under `vscode-extensions/`. | No Sphinx configuration interface; depends on packaged resources, subprocesses, and platform behavior. | No command-specific test found in the current test tree. | Good isolated feature after resource access and subprocess behavior have clear ownership. |
| `hb htaccess groups/members` | CLI commands in `__main__.py`; behavior delegated to `web_access_ctrl` modules. | No Sphinx configuration interface and little CLI-side configuration coupling. | No direct CLI test found; the broader `test-htaccess.bats` covers build output rather than these queries. | Low-coupling commands; can move separately from `htaccess update`. |
| `hb htaccess update` | CLI command in `__main__.py`; uses Kconfig paths, a packaged YAML template, and `web_access_ctrl.create_htaccess_entries`. | Uses project config and affects generated publish access files; related Sphinx behavior also exists in `conf.py`. | `tests/e2e/test-htaccess.bats` exercises generated build output. | Keep distinct from the query commands; its config and output-path dependencies make it a later step. |
| `hb tools install/check/check-scoop` | CLI commands in `__main__.py`; external tool metadata in `external_tools.json`; Scoop helpers in the same module. | No Sphinx configuration interface, but shares package resources and external-tool resolution. | A Linux-gated test in `tests/test_hermesbaby.py` exercises install/check. | Move as one feature after tool resolution and installation responsibilities are defined. |
| `hb ci install-tools/run` | CLI commands in `__main__.py`; scripts under `ci/`. | No Sphinx configuration interface; depends on packaged scripts, platform checks, and process execution. | CI end-to-end coverage exists for selected workflows. | Separate from `ci config-to-env`; script/resource packaging is the main concern. |
| `hb configure` | CLI command in `__main__.py`; loads Kconfig and starts `menuconfig` or `guiconfig`. | No Sphinx config execution, but it owns the configuration state consumed by most other commands. | Windows batch test exercises it; no focused automated test identified. | Foundational configuration functionality; extract with the shared config service rather than as an isolated command. |
| `hb clean` and `hb venv` | CLI commands in `__main__.py`; both read Kconfig; `venv` also manages an environment and optional requirements installation. | No direct Sphinx config interface; depend on project paths from Kconfig. | No focused tests identified. | Migrate after the config-loading boundary is established. Keep separate use cases. |
| `hb publish` | CLI command in `__main__.py`; reads Kconfig, Git state, SSH configuration, and `out/docs/html`. | Depends on build output and project configuration, but does not configure Sphinx. | No focused publish test identified. | Later CLI feature; verify remote side effects carefully and preserve the public command contract. |
| `hb text/html/html-live/pdf/pdf-live` | CLI adapters and `_build_common()` in `__main__.py`; invokes Sphinx or sphinx-autobuild. | Directly crosses the `CONFIG_*` environment boundary into the top-level Sphinx `conf.py`. | Multiple build E2E tests, including partial builds, language overrides, i18n, and CI builds. | Migrate after the shared build runner and Sphinx configuration contract are agreed. Keep shared behavior shared. |
| `hb i18n gettext/update-po/stats/stats-summary` | CLI commands and report parsing in `__main__.py`; invokes Sphinx gettext and `sphinx-intl`. | Direct dependency on the build runner, Sphinx gettext settings, locale paths, and Kconfig values. | `tests/e2e/test-i18n.bats` and `tests/e2e/test-ci-i18n.bats`. | Later than the basic build path; keep the four related commands and their shared stat behavior together. |
| `hb version` | Typer callback in `__main__.py`. | No Sphinx or project-config dependency. | CLI behavior is small and straightforward. | Keep as entry-point wiring unless the CLI layout requires moving it. |

## Sphinx configuration and authoring functionality

The following are current configuration responsibilities to map to feature
owners. The list does not imply that their existing extension directories
should move or change.

| Responsibility | Current surface | Migration notes |
| --- | --- | --- |
| Project metadata, language, general settings, and path helpers | Top-level `conf.py`; values are derived from the `CONFIG_*` snapshot and HermesBaby environment variables. | Establish shared configuration context and ordering rules before extracting dependent settings. |
| HTML theme and static/template behavior | Top-level `conf.py`, `html_static/`, and `theme_templates/`. | Keep assets in place; move only HermesBaby-specific configuration ownership. |
| LaTeX/PDF settings | Top-level `conf.py`, including a large set of LaTeX options and setup hooks. | A candidate for an early Sphinx-configuration extraction after the hook/context contract is implemented. |
| Published-document access control | CLI `htaccess update`, `htaccess.yaml`, and related settings/hooks in `conf.py`. | Shared concern spans command behavior and Sphinx output; map both parts under one feature without conflating their layers. |
| Authoring extensions and their settings | Top-level `conf.py` plus existing directories such as `drawio/`, `partly/`, `loflot/`, `rst-frontmatter/`, `tag-anything/`, and `toctree-only/`. | Existing extension directories remain untouched. Move only registration and HermesBaby-specific settings into feature-owned `conf.py` hooks. |
| Bibliography, intersphinx, Jupyter, Mermaid, Graphviz, and other extension settings | Top-level `conf.py` and third-party extensions. | Inventory settings, dependencies, and ordering before assigning feature ownership; not every third-party extension needs a HermesBaby feature package. |
| Translation configuration | Top-level `conf.py` and the `hb i18n` commands. | Keep locale configuration and i18n CLI behavior under a coherent feature while preserving the shared build service. |

## Provisional order

The sequence starts with `hb new`, as the clearest user-facing functionality
without a Sphinx-configuration interface. It should be finalized only after
the architecture interfaces and dependency inventory have been agreed.

1. **`hb new`.** It has no Sphinx-config interface, built-in Cookiecutter
contexts need only `directory`, and there is focused E2E coverage. Inspect
whether `_set_env()` and `_load_config()` are unnecessary for this command;
retain an explicit dependency on packaged-template lookup and Cookiecutter.
2. **`hb ci config-to-env`.** A small follow-up extraction: the command
   delegates to `hermesbaby.ci.parse_config` and does not load Kconfig or
   touch Sphinx. Add a focused CLI test because current coverage does not
   appear to exercise the command directly.
3. **`hb vscode check/install/uninstall`.** The commands form a coherent
   feature with packaged recommendation data and subprocess interactions, but
   need focused tests around those boundaries.
4. **`hb htaccess groups/members`.** These commands are low-coupling and
   already delegate to separate modules. Move them separately from the
   config-dependent `htaccess update` command.
5. **Tool management and CI script commands.** Move external-tool resolution,
   Scoop behavior, and packaged CI scripts with their resource and platform
   dependencies made explicit.
6. **Configuration-dependent local commands:** `configure`, `clean`, and
   `venv`. First establish the shared configuration service used by these
   commands and other features.
7. **`htaccess update` and `publish`.** These depend on project paths,
   generated build output, or both; preserve their file and remote side
   effects with focused tests.
8. **Build commands and shared build orchestration.** Keep `text`, `html`,
   `html-live`, `pdf`, and `pdf-live` as separate user interfaces over
   genuinely shared application behavior. Validate the `CONFIG_*` handoff.
9. **i18n commands.** Move after the build service and Sphinx configuration
   contract are stable because extraction and catalog maintenance depend on
   both.
10. **Sphinx configuration responsibilities.** Once the hook mechanism is
    tested, extract settings in dependency-aware groups: begin with a
    self-contained part such as LaTeX/PDF or htaccess, then theme/output
    settings, then ordered extension settings. The exact order depends on
    the shared-context dependency map.

## Questions to resolve before implementation

- Is `ci config-to-env` an acceptable technical rehearsal before `hb new`,
  or should the first moved command be `hb new` itself?
- Which shared configuration and resource APIs are part of the application
  layer, and which remain internal to the CLI entry point?
- Which Sphinx configuration sections depend on settings initialized by
  earlier sections, and what order must the feature hooks preserve?
- Which commands need new focused tests before extraction because current
  coverage is absent or indirect?
