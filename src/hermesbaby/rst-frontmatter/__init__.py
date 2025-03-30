"""
# Sphinx reST Frontmatter Extension

This Sphinx extension enables YAML frontmatter support in reStructuredText (`.rst`) files.

## Frontmatter Format

Frontmatter must be written as an indented block comment at the top of the `.rst` file:

```rst
..
   ---
   title: My Title
   author: Alex
   template: true
   items:
     - Item A
     - Item B
     - Item C
   ---
```

## What It Does

- Parses the YAML block
- Removes it from the source before parsing
- Injects variables into the Jinja context (only if `template: true` is set)
- Optionally injects simple values into `rst_prolog` as substitutions
- Supports global substitutions via `rst_prolog_substitutions`
- Optionally loads substitutions from an external YAML file via `rst_prolog_substitutions_yml_file`

## Usage Examples

### Variable Access

If the above frontmatter is used, the variables `title`, `author`, and `template` will be available:

```jinja
{{ title }}  →  My Title
```

In `.rst`, they can be referenced as substitutions:

```rst
|title| → My Title
```

### Jinja Conditional Example

```jinja
{% if feature_enabled %}
This feature is enabled.
{% else %}
This feature is disabled.
{% endif %}
```

### Jinja Loop Example

```jinja
{% for item in items %}
- {{ item }}
{% endfor %}
```

## Configuration Options

**`rst_prolog`**  
Built-in Sphinx config value. This extension appends reST substitution definitions
(e.g., `.. |key| replace:: value`) when `template: true` is set in the frontmatter.

**`rst_prolog_substitutions`**  
A global dictionary of substitutions (like `myst_substitutions`).
Used in all templated `.rst` files. Overridden by YAML file and frontmatter.

**`rst_prolog_substitutions_yml_file`**  
Optional path to a YAML file. If it exists, it is loaded and used for substitutions.
Its values override `rst_prolog_substitutions`, but are overridden by file-local frontmatter.
If the file is specified but missing, a log message is shown at the start of the build.

## Substitution Precedence

This extension merges substitutions from three sources. Precedence is (lowest to highest):

1. `rst_prolog_substitutions` (global dictionary in `conf.py`)
2. `rst_prolog_substitutions_yml_file` (optional external YAML file)
3. File-local YAML frontmatter

Values defined in the file frontmatter override those from the YAML file, which override those from `rst_prolog_substitutions`.
"""

import os
import re
import yaml
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

FRONTMATTER_PATTERN = re.compile(
    r"^\.\.\s*\n((?:\s{3,}.+\n)+)", re.MULTILINE
)

_loaded_yaml_substitutions = {}

def parse_yaml_frontmatter(block: str) -> dict:
    lines = [line[3:] if line.startswith("   ") else line for line in block.splitlines()]
    if lines[0].strip() == '---':
        try:
            end_idx = lines.index('---', 1)
            yaml_lines = lines[1:end_idx]
            return yaml.safe_load("\n".join(yaml_lines)) or {}
        except ValueError:
            logger.warning("Missing closing '---' in YAML frontmatter block")
        except yaml.YAMLError as e:
            logger.warning(f"YAML parse error in frontmatter: {e}")
    return {}

def on_config_inited(app: Sphinx, config):
    global _loaded_yaml_substitutions
    path = app.config.rst_prolog_substitutions_yml_file
    if path:
        if os.path.exists(path):
            try:
                with open(path, encoding='utf-8') as f:
                    _loaded_yaml_substitutions = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Could not read YAML substitutions file '{path}': {e}")
        else:
            logger.info(f"YAML substitutions file '{path}' not found — you may create it to define shared substitutions.")

def on_source_read(app: Sphinx, docname: str, source: list[str]) -> None:
    content = source[0]
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return

    comment_block = match.group(1)
    metadata = parse_yaml_frontmatter(comment_block)
    if not metadata:
        return

    source[0] = content[match.end():].lstrip('\n')

    env = app.env
    if not hasattr(env, 'rst_frontmatter'):
        env.rst_frontmatter = {}
    env.rst_frontmatter[docname] = metadata

    if metadata.get("template"):
        combined = dict(app.config.rst_prolog_substitutions or {})
        combined.update(_loaded_yaml_substitutions)
        combined.update(metadata)
        for key, value in combined.items():
            if isinstance(value, (str, int, float)):
                app.config.rst_prolog += f"\n.. |{key}| replace:: {value}"

def inject_jinja_context(app: Sphinx, pagename: str, templatename: str, context: dict, doctree):
    metadata = getattr(app.env, 'rst_frontmatter', {}).get(pagename, {})
    if metadata.get("template"):
        context.update(app.config.rst_prolog_substitutions or {})
        context.update(_loaded_yaml_substitutions or {})
        context.update(metadata)

def setup(app: Sphinx):
    app.connect("config-inited", on_config_inited)
    app.connect("source-read", on_source_read)
    app.connect("html-page-context", inject_jinja_context)
    app.add_config_value("rst_prolog", "", "env")
    app.add_config_value("rst_prolog_substitutions", {}, "env")
    app.add_config_value("rst_prolog_substitutions_yml_file", None, "env")
    return {
        "version": "0.4",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
