# Title of Root Document

This document mixes "filesystem" toctree mode (see .hermesbaby) with an
explicit ```{toctree}``` directive below, which belongs to "directive" mode.
The directive is redundant with the filesystem-derived _toc.yml, so it is
tolerated and neglected (silently dropped) instead of failing the build.

```{toctree}
child
```
