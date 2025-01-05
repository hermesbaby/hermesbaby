<!---
################################################################
#                                                              #
#  This file is part of HermesBaby                             #
#                       the software engineer's typewriter     #
#                                                              #
#      https://github.com/hermesbaby                           #
#                                                              #
#  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
#                                                              #
#  License(s)                                                  #
#                                                              #
#  - MIT for contents used as software                         #
#  - CC BY-SA-4.0 for contents used as method or otherwise     #
#                                                              #
################################################################
-->

# Toctree-Only

Inspired by https://stackoverflow.com/questions/15001888/conditional-toctree-in-sphinx

## Configuration

`conf.py`:

```
extensions = [
    'toctree_only',
    # other extensions
]
```

Usage inside a reStructuredText file:

```
.. toctree-only::
    :maxdepth: 2
    :caption: Contents:

    env_html : introduction
    env_latex and env_pdf : usage
    env_singlehtml or not env_html : advanced
    anotherdoc
```
