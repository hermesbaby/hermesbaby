---
status: accepted
decided: 2026-10-18
---

# Use explicit hooks for feature-owned Sphinx configuration

## Context and Problem Statement

HermesBaby's Sphinx configuration is concentrated in a large `conf.py`.
The architecture refactoring needs a way for feature-owned configuration
files to contribute Sphinx settings while keeping the top-level `conf.py`
as the entry point passed to Sphinx.

The existing Sphinx extension directories are standard extensions and assets.
The refactoring should move HermesBaby-specific configuration without
changing those directories.

## Decision Outcome

Chosen: each feature that contributes Sphinx configuration may own a
`conf.py` under `features/<feature>/`. The top-level Sphinx configuration
will include each feature through an explicit hook, such as
`configure(context)`, in a defined order.

Feature configuration will not be loaded by executing source code into the
entry configuration's globals. The hook will receive a shared context; its
exact API is to be agreed as part of the architecture design before feature
migration.

The existing standard Sphinx extension and asset directories remain
unmodified by this refactoring.

## Consequences

- Good: feature configuration has an explicit ownership and invocation
  boundary while Sphinx continues to use the existing top-level `conf.py`.
- Good: feature ordering and the values available to each feature can be
  made explicit and tested.
- Good: standard Sphinx extension directories remain independent of
  HermesBaby's configuration refactoring.
- Follow-up: define and test the shared context API, ordering rules, user
  `conf.py` override behavior, and setup-hook registration before moving
  existing feature configuration.
