# Weaknesses addressed by the planned design

| Current weakness | Planned response |
| --- | --- |
| CLI registration and command behavior are concentrated in `__main__.py`. | Keep the CLI layer thin and move use-case behavior into feature-owned application modules or shared application services. |
| Sphinx settings for unrelated features are concentrated in `conf.py`. | Keep `conf.py` as the Sphinx entry point and delegate feature settings to feature-owned `conf.py` modules through explicit hooks. |
| The boundary between CLI, application behavior, and Sphinx configuration is unclear. | Define CLI, application, and Sphinx configuration layers with explicit dependency rules. |
| Sphinx configuration relies on a flat namespace and ordering. | Make feature order explicit and provide a shared context for the resolved snapshot, assembled settings, helpers, and setup hooks. |
| It is difficult to tell where a feature's code belongs. | Give each feature the parts it needs under `features/`, without requiring empty modules or moving standard Sphinx extensions. |
| A broad refactor would be difficult to verify. | Agree on the architecture first, inventory and order functionalities, then migrate one independently testable functionality at a time. |

These are intended responses, not claims that implementation is complete.
Each row should be revisited as the feature inventory and migrations provide
evidence.
