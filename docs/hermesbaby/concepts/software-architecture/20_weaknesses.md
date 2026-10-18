# Weaknesses of the current architecture

These are the problems the refactoring aims to address. The feature inventory
will validate and refine them before migration begins.

- **Responsibilities are concentrated.** The CLI entry point mixes command
  wiring with behavior, while the Sphinx configuration combines settings and
  hooks for many unrelated concerns.
- **Feature ownership is unclear.** A change to one user-visible
  functionality may require navigating a large shared file instead of a
  clearly owned feature module.
- **Boundaries are difficult to see.** CLI behavior, reusable application
  logic, and Sphinx-specific configuration are not consistently separated.
- **Ordering and shared state can be implicit.** Sphinx settings are
  calculated in a flat configuration namespace, and later sections may rely
  on values prepared earlier. The order and dependencies are not represented
  as feature-level interfaces.
- **The organization does not guide incremental change.** There is no
  consistent place to put the CLI, application logic, and Sphinx
  configuration for a feature when those parts are present.

The target is not to eliminate all shared code. Shared behavior belongs in a
shared layer when multiple features genuinely use it; the goal is to make
those dependencies explicit and keep unrelated feature changes local.
