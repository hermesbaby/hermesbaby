# Title of Root Document

This document mixes "filesystem" toctree mode (see .hermesbaby) with an
explicit ```{toctree}``` directive below, which belongs to "directive" mode.
sphinx-external-toc does not tolerate that combination: it raises
"toctree directive not expected with external-toc" for any document that
still contains one, which hermesbaby's default -W (warn-as-error) build
turns into a hard failure.

```{toctree}
child
```
