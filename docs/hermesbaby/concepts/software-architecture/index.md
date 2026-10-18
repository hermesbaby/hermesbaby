# Software architecture

This concept documents the architecture refactoring of HermesBaby. The goal
is to make feature changes local: a feature should own its command-line
interface, application behavior, and Sphinx configuration where those parts
exist.

The work is deliberately staged. First agree on the target architecture and
its boundaries. Then inventory the existing functionalities, understand their
dependencies, and decide a migration order. Only after that should existing
features be moved.

```{toctree}
:numbered:

10_current_architecture
20_weaknesses
30_planned_architecture
40_migration
50_addressed_weaknesses
60_feature_inventory
```

Architecture decisions are recorded separately in
`docs/hermesbaby/decisions/`.
