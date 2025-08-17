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

# sphinx_loflot

## Summary

`sphinx_loflot` is a lightweight Sphinx extension that adds **two new directives**:

- `.. list-of-figures::`
- `.. list-of-tables::`

It works for **HTML and other non-LaTeX builders**.
For LaTeX/PDF builds, it plays nicely with LaTeX’s native “List of Figures” and “List of Tables”.

The extension follows the principle:

> **As simple as possible, as sophisticated as needed.**

---

## Purpose

Out-of-the-box, Sphinx provides:

- `.. contents::` → Table of Contents
- `.. toctree::` → Document structure
- `:numref:` → Cross-references to figures and tables

But **there’s no way to generate a full “List of Figures” or “List of Tables” in HTML**.
This extension closes that gap with minimal code and without over-engineering.

---

## How to Use

1. **Enable the extension**

   In your `conf.py`:

   ```python
   import os, sys
   sys.path.append(os.path.abspath("_ext"))

   extensions += ["sphinx_loflot"]

   numfig = True  # optional: enables numbering (e.g. "Figure 1.2")

   # Defaults (customize if needed)
   loflot_include_uncaptioned_figures = True
   loflot_include_uncaptioned_tables  = True
   loflot_uncaptioned_label_figure    = "[No caption]"
   loflot_uncaptioned_label_table     = "[No title]"

   # Control behavior for LaTeX builder
   # 'passthrough' (default): emit LaTeX-native \listoffigures / \listoftables
   # 'duplicate'            : render our bullet list even for LaTeX
   loflot_latex_behavior = "passthrough"
   ```

2. **Insert a list into your docs**

````markdown
```{list-of-figures}
```

```{list-of-tables}
```
````


You can override the Default Configuration and the configuration in `conf̀.py` via the options

````markdown
```{list-of-figures}
:caption: Figures in this Documentation
:include-uncaptioned: true
:uncaptioned-label: [No caption]
```

```{list-of-tables}
:caption: Tables in this Documentation
:include-uncaptioned: true
:uncaptioned-label: [No title]
```
````

3. **Build your docs**

   ```bash
   make html
   ```

   You’ll see linked lists of figures/tables wherever you placed the directives.

---

## How It Works

- On `doctree-read`:
  Traverses the document tree, collecting all `nodes.figure` and `nodes.table` with their anchors, captions, and (optionally) numbers.

- On `doctree-resolved`:
  Replaces the placeholder `list-of-figures` / `list-of-tables` nodes with generated bullet lists containing links to the collected items.

- Supports caption-less figures/tables:
  When enabled, placeholder labels (configurable) are used.

- Plays nice with parallel and incremental builds:
  Implements `env-purge-doc` and `env-merge-info` hooks.

---

## What Might Be Extended

Future extensions could include:

- **Filtering**: Show only figures/tables from a specific document or section.
- **Grouping**: Group lists by document, chapter, or section.
- **Sorting**: Order by document order (default), by caption text, or by number.
- **Validation**: Warnings for caption-less figures/tables when they should have captions.
- **Custom output formats**: For example, export the list as JSON or YAML for external tooling.

---

## How to Extend Technically

The extension is deliberately simple and modular. Here’s the walkthrough:

1. **Directives**

   - `ListOfFigures` and `ListOfTables` directives create placeholder nodes.
   - Options (`:caption:`, `:include-uncaptioned:`, `:uncaptioned-label:`) are stored on the node.

2. **Custom Nodes**

   - `list_of_figures_node` and `list_of_tables_node` are custom node types that mark where the lists should be inserted.

3. **Event Hooks**

   - `doctree-read`: Traverse the doctree, collect `nodes.figure` / `nodes.table`, extract `caption` or `title`, assign anchor IDs.
   - `env-purge-doc`: Remove items from a document when it’s rebuilt.
   - `env-merge-info`: Merge results from parallel builds.

4. **List Building**

   - On `doctree-resolved`, the collected items are formatted into a `bullet_list`.
   - Each entry contains:
     - Number (if available from `numfig`)
     - Link (`make_refnode`) to the figure/table
     - Caption or placeholder

5. **Configuration**

   - `loflot_include_uncaptioned_figures` / `tables`: Whether to list caption-less items.
   - `loflot_uncaptioned_label_figure` / `table`: Placeholder labels.
   - These can be overridden per directive with options.

6. **Return Values**

   - `setup()` registers directives, nodes, event hooks, and config values.
   - Declares `parallel_read_safe` and `parallel_write_safe` for performance.

---

## Design Principle

> **As simple as possible, as sophisticated as needed.**
>
> This extension provides the missing “List of Figures” and “List of Tables” functionality without unnecessary complexity.
> New features will be added only when proven necessary, keeping the implementation clean and maintainable.

