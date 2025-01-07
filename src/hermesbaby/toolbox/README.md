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
--->

# Toolbox

## Reference Sanitizer

Meant to be called manually from time to time.

```bash
poetry run python sphinx-contrib/toolbox/src/toolbox/reference_sanitizer.py docs/ --dry-run
```

```bash
poetry run python sphinx-contrib/toolbox/src/toolbox/reference_sanitizer.py docs/ --force
```


## Generate atom feed

Meant to be integrated into (html-) build.

TODO: Rename it because name doesn't fit anymore.

```bash
poetry run python \
   sphinx-contrib/toolbox/src/toolbox/generate_atom_feed.py \
    --rss-feed-path docs/web_root/feed.rss \
    --rst-file-path docs/autogenerated/changes.rst
```

```bash
poetry run python \
   sphinx-contrib/toolbox/src/toolbox/generate_atom_feed.py \
    --atom-feed-path docs/web_root/feed.atom \
    --rst-file-path docs/autogenerated/changes.rst
```
