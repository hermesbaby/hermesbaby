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

# Partly - Build Parts of Documents

The `partly` extension for Sphinx allows you to build partial documentation even when some cross-references are undefined. This is useful during incremental documentation development or when working on specific sections of large documentation projects.

## Features

### Graceful Handling of Undefined References

Instead of failing the build when cross-references cannot be resolved, `partly` automatically:

1. **Allows the build to continue** - Undefined references don't stop document generation
2. **Works with strict builds** - Compatible with `sphinx-build -W` (treat warnings as errors)
3. **Creates a summary table** - Appends an "Undefined References" section at the end of documents that contain unresolved cross-references
4. **Defines target anchors** - Creates targets for undefined labels in the table, so the structure is in place for when they're defined
5. **Reports undefined references** - Logs all unresolved references at the end of the build

### Build with `-W` Flag Support

The `partly` extension is specifically designed to work with `sphinx-build -W` (or `warningiserror = True` in config), which treats all warnings as errors. This is crucial for CI/CD pipelines and strict documentation builds.

**Without `partly`:**
```bash
$ sphinx-build -W docs build
Warning, treated as error:
doc.md:9: Failed to create a cross reference. A title or caption not found: 'undefined_label'
Sphinx exited with exit code: 2
```

**With `partly`:**
```bash
$ sphinx-build -W docs build
The build contains the following unresolved cross-reference(s):
  - undefined_label
build succeeded.
```

The build succeeds, and undefined references are documented in the output with a table showing what's missing.

### Undefined References Table

When a document contains references to undefined labels, `partly` automatically appends a section at the end titled "Undefined References". This section contains:

- **A descriptive paragraph** explaining that some cross-references couldn't be resolved
- **A table listing each reference occurrence**:
  - **Label**: The undefined label name
  - **Document**: The source document where this reference appears

**Important**: Each row in the table represents a specific cross-reference occurrence, not just unique labels. If the same undefined label is referenced multiple times, there will be multiple rows (one for each reference).

#### Example Output

If your document contains:
```rst
See :ref:`missing_section` for details.
Also check :ref:`missing_section` later.
And :ref:`another_missing` too.
```

The table will show 3 rows:

```
Undefined References
====================

The following cross-references could not be resolved:

+-------------------+------------+
| Label             | Document   |
+===================+============+
| another_missing   | index      |
+-------------------+------------+
| missing_section   | index      |
+-------------------+------------+
| missing_section   | index      |
+-------------------+------------+
```

Note that `missing_section` appears twice because it was referenced twice in the document.

## Usage

Add `hermesbaby.partly` to your Sphinx `extensions` list in `conf.py`:

```python
extensions = [
    'hermesbaby.partly',
    # ... other extensions
]
```

## Behavior Details

### What Counts as Undefined

A reference is considered undefined when:
- The target label doesn't exist anywhere in the documentation source
- The reference uses the `:ref:` role with a label that hasn't been defined

### What Doesn't Trigger the Table

The following scenarios do NOT create undefined reference entries:
- **Forward references**: References to labels defined later in the same document
- **Cross-document references**: References to labels in other documents (as long as they exist)
- **Non-`std` domain references**: Only standard domain (`:ref:`) references are tracked

### Build Reporting

At the end of each build, `partly` logs a summary of all undefined references:

```
The build contains the following unresolved cross-reference(s):
  - missing_section
  - undefined_api
```

This appears in the build log/info output, making it easy to track what needs to be defined.

## Implementation Notes

- The extension uses a custom Sphinx Transform (`CollectPendingXrefs`) that runs before cross-reference resolution to capture all `pending_xref` nodes
- This allows tracking of every reference occurrence, not just unique labels (Sphinx caches resolution per unique label)
- The extension hooks into Sphinx's `missing-reference` event to identify which references are undefined
- Returns a reference node (instead of None) to prevent Sphinx from emitting warnings, allowing `-W` builds to succeed
- Dummy labels are registered during cross-reference resolution pointing to the source document
- The "Undefined References" section is appended in the `doctree-resolved` event after resolution
- Target anchors are created with IDs matching the undefined label names
- The reference nodes created include proper `refuri` attributes pointing to `#{label_name}`
- Global tracking lists are cleared after each build to prevent accumulation

## Version

Current version: 0.2
