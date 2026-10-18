# Planned architecture

## Layers

1. **CLI layer** parses arguments, invokes application behavior, and presents
   results. It owns Typer-specific command definitions.
2. **Application layer** implements use cases such as building, creating a
   project, publishing, or managing tools. It does not depend on Typer or
   Sphinx. Shared behavior belongs here when more than one command needs it.
3. **Sphinx configuration layer** assembles the Sphinx configuration from
   the `CONFIG_*` environment snapshot and feature-owned configuration
   modules. It does not load Kconfig.

The application layer is the layer between the CLI and Sphinx configuration;
it is not another name for the build layer. A build is one application use
case and may invoke Sphinx.

## Feature ownership

HermesBaby-specific functionality will be organized under `features/` where
that helps establish clear ownership. A feature may have a CLI part, an
application part, a Sphinx configuration part, or only the parts it needs.
The layout should not require empty modules for absent parts.

Each feature that contributes Sphinx settings will have a `conf.py` under its
feature directory. The Sphinx entry configuration will call an explicit hook
from each feature configuration, for example `configure(context)`, in a
documented order. Feature configuration will not be loaded by executing
arbitrary source into the entry configuration's globals.

The shared context should expose the resolved configuration snapshot, common
path helpers, the Sphinx settings being assembled, and the collected
`setup(app)` hooks. The entry configuration remains responsible for exposing
the assembled settings through Sphinx's expected configuration namespace.
The exact context API should be agreed before feature migration.

## Proposed package layout

```text
hermesbaby/
   __main__.py                 # installed entry point and composition root
   features/
      new/
         cli.py                  # hb new command registration
         service.py              # project creation behavior
      html/
         cli.py                  # optional build command registration
         service.py              # optional build use case
         conf.py                 # optional Sphinx configuration hook
```

The example is illustrative, not a requirement that every feature contain
all three modules. Existing standard Sphinx extension and asset directories
remain where they are; a feature's `conf.py` may configure or register them
without moving their code.

## Composition and feature contracts

- `__main__.py` owns the root Typer app, command ordering, and explicit
   imports/registration of CLI features. Keep the installed `hb` and
   `hermesbaby` entry points stable. Do not introduce dynamic plugin discovery
   or a general feature registry unless a concrete need appears.
- A feature's `cli.py` owns its Typer command declarations and adapts
   arguments, output, and exit behavior to its application functions. It may
   use Typer; it should not become the home of reusable use-case logic.
- A feature's `service.py` owns that feature's application behavior. It
   accepts explicit inputs and returns results or raises application-level
   errors; it does not import Typer or Sphinx. Shared application code is
   extracted only when there is actual reuse.
- A feature's Sphinx `conf.py` exports a plain function such as
   `configure(context)`. The top-level Sphinx `conf.py` calls these functions
   in an explicit, tested order. No base `Feature` class is needed for this
   contract.
- A candidate `SphinxConfigContext` contains the resolved `ConfigCompat`
   snapshot, the Sphinx settings being assembled, and the ordered
   `setup(app)` callbacks. Feature hooks read and update settings through this
   context. The ordered `extensions` value is part of those settings.
- Use a context object because configuration and callbacks are shared mutable
   state across ordered hooks. Do not add a base class, feature registry, or
   class hierarchy for the hooks themselves.
- Shared Sphinx path/configuration helpers should have one common
   implementation; feature hooks should not duplicate them. Their exact
   placement can be settled with the context API.
- The Sphinx entry configuration owns final publication of assembled
   settings into Sphinx's flat configuration namespace. It reads the
   `CONFIG_*` snapshot and does not load Kconfig.
- The optional project `conf.py` currently receives a proxy `app` and
   `extensions` list, along with `roles` and `nodes`. Preserve extension
   additions, role registration, and proxy-app calls while introducing the
   built-in feature hooks. This bridge does not currently merge arbitrary
   user-conf globals into HermesBaby's Sphinx settings.

## Sphinx configuration lifecycle

The proposed entry-conf assembly order is:

1. Read the `CONFIG_*` snapshot and initialize shared helpers and baseline
   Sphinx settings, including the ordered `extensions` list.
2. Call built-in feature `configure(context)` hooks in an explicit order.
   Each hook may update the shared settings and append `setup(app)` callbacks.
3. Evaluate the optional project `conf.py` with the existing extension/role/
   node API and proxy `app`. Preserve extension additions and record proxy
   calls; do not treat arbitrary names in that file as overrides of the
   assembled HermesBaby settings.
4. Publish the assembled settings through the top-level `conf.py` namespace
   for Sphinx to consume.
5. When Sphinx invokes `setup(app)`, call built-in feature setup callbacks
   in their declared order, then replay the project-conf proxy-app calls in
   their original order.

Add an integration test that exercises a project config adding an extension,
registering a local role, and making a proxy-app call. There is currently a
fixture for this behavior, but no test was found that references it. Any
broader user-conf override behavior should be specified and tested separately
before being promised as part of the refactoring.

## Dependency rules

- CLI modules may depend on their feature's application service and shared
   application utilities.
- Application services may depend on shared application utilities and
   feature data/resources, but not on Typer or Sphinx.
- Sphinx configuration hooks may depend on the Sphinx configuration context
   and Sphinx APIs, but not on Typer or Kconfig loading.
- Cross-feature dependencies should be explicit. If behavior is genuinely
   shared, place it in an application-level module rather than importing one
   feature's CLI or configuration module from another feature.
- Resource lookup should have one deliberate owner so features do not
   duplicate development, installed-package, and frozen-build path logic.

## First migration boundary: `hb new`

`hb new` is a useful first feature because it has no Sphinx configuration
part. Its CLI module should preserve the current options and user-visible
messages while delegating template validation and project creation to its
application service. The service should receive the template root explicitly
or use a shared package-resource utility; it should not load Kconfig merely
because the current command does so. Confirm that removing `_set_env()` and
`_load_config()` preserves behavior before making that change. Existing
Cookiecutter templates and their files stay in place.

## Decisions still open

- Confirm the context's final fields and whether feature hooks mutate its
   settings mapping or return settings to merge.
- Decide where shared Sphinx path helpers live and how hooks access them.
- Verify user `conf.py` extension additions, role registration, and proxy-app
   calls with an integration test before changing how setup calls are
   collected or replayed.

## Compatibility constraints

- Keep the top-level `conf.py` as the Sphinx `-c` entry point.
- Keep Kconfig loading in the CLI/application startup path. Sphinx receives
  only the exported `CONFIG_*` snapshot.
- Preserve the currently supported user `conf.py` integration behavior and
   Sphinx setup-hook ordering; broader setting overrides require a separate
   decision and tests.
- Keep existing standard Sphinx extension and asset directories unmodified
  by this refactoring.
- Apply object-oriented design only where objects make state, lifecycle, or
  substitutable behavior clearer. Do not add a base class or registry solely
  to make the architecture look object-oriented.
