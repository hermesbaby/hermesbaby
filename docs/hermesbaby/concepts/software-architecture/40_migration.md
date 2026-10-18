# Migration approach

The architecture should be agreed before existing features are moved. This
keeps the refactoring from turning into a sequence of local rearrangements
without a shared destination.

## Stages

1. **Agree on the architecture.** Confirm the layer responsibilities,
   feature ownership, Sphinx configuration hook, shared context, and
   compatibility constraints.
2. **Inventory the functionality.** List user-visible CLI commands,
   authoring features, build outputs, and shared services. For each, record
   its current files, dependencies, tests, and whether it crosses the
   Sphinx configuration boundary.
3. **Order the migrations.** Use the inventory to identify dependencies and
   choose small, independently verifiable steps. Prefer functionalities
   with few dependencies and no Sphinx configuration interface first.
4. **Migrate incrementally.** Move one functionality at a time, preserve
   behavior and public command interfaces, and run focused tests after each
   step.
5. **Review the architecture.** Update the design and decisions when
   implementation evidence shows that a boundary or shared abstraction
   should change.

## Initial ordering hypothesis

`hb new` is a candidate for an early migration because it is expected not to
depend on the Sphinx configuration layer. Confirm that dependency profile in
the inventory before fixing the order. The complete migration list is an
output of stage 3, not a precondition for agreeing on the architecture.

## Migration safeguards

- Establish the existing test baseline before moving functionality.
- Keep command names, options, exit behavior, and build environment handoff
  stable unless a separate decision explicitly changes them.
- Preserve the rule that CLI/application startup resolves Kconfig and the
  Sphinx child process consumes the `CONFIG_*` snapshot.
- Test Sphinx configuration assembly, user `conf.py` extension additions,
  role registration, proxy-app calls, and `setup(app)` hook ordering when
  changing the Sphinx configuration layer. Treat broader user setting
  overrides as a separate behavior unless explicitly specified and tested.
- Verify that feature configuration files and other required resources are
  present in both Python package and frozen builds.
- Do not modify the existing standard Sphinx extension directories as part
  of this refactoring.
