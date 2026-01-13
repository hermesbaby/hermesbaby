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

### Automatic Bibliography Injection

When citations are used but no bibliography directive is found, `partly` can automatically:

1. **Detect missing citations** - Handles missing bibtex keys gracefully instead of failing the build
2. **Create dummy citations** - Registers placeholder citation entries to prevent "not found" warnings
3. **Inject bibliography chapter** - Creates a top-level "Injected Bibliography" chapter in the root document
4. **Enable citation builds** - Allows builds with unresolved citations to succeed with `-W` (warnings as errors)

This is useful when working on document fragments that use citations without maintaining the full bibliography structure.

#### How It Works

The extension leverages Sphinx's build phases intelligently:

**Key Insight**: Citations can appear before the bibliography directive in the same document without warnings, because validation happens AFTER all parsing is complete.

**Implementation**:
1. **Early Scanning** (`env-before-read-docs`): Detect if citations exist and if bibliography directive is present
2. **Post-Parse Injection** (`env-updated`): After ALL documents are parsed but BEFORE citation validation:
   - Check if bibliography directive was found anywhere
   - If not, inject bibliography into the root document's doctree
   - This happens at the perfect moment - after parsing (so we don't modify source) but before validation (so citations resolve)
3. **Normal Validation**: sphinxcontrib-bibtex validates citations against the injected bibliography
4. **Real Warnings**: Only actual missing keys in the .bib file produce warnings

This approach ensures:
- ✅ No source code modification (works at doctree level)
- ✅ Bibliography present before validation (no false warnings)
- ✅ Real missing keys still generate appropriate warnings
- ✅ Works with `-W` when .bib file is complete

Example with `-W` flag (warnings as errors):

```bash
$ sphinx-build -W docs build
```

Without `partly`, this would fail with:

```
Warning, treated as error:
docs/index.md:5: could not find bibtex key "Smith2023"
```

With `partly`, the build succeeds and the bibliography is injected automatically.

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

- **A main section** with the configurable title (default: "Outgoing Cross-References")
- **Subsections for each reference type** encountered:
  - `Cross-references (ref)` - for `:ref:` references
  - `Glossary terms (term)` - for `:term:` references
  - `Documents (doc)` - for `:doc:` references
  - And other standard Sphinx reference types
- **A table within each subsection** listing reference occurrences:
  - **Label**: The undefined label name
  - **Used In**: Where the reference appears (chapter and source file)

**Important**: Each row in the table represents a specific cross-reference occurrence, not just unique labels. If the same undefined label is referenced multiple times, there will be multiple rows (one for each reference).

#### Example Output

If your document contains:

```rst
See :ref:`missing_section` for details.
Also check :term:`missing_term` in the glossary.
And :ref:`another_missing` too.
```

The output will show separate subsections:

```text
Outgoing Cross-References
==========================

Cross-references (ref)
----------------------

+-------------------+------------+
| Label             | Used In    |
+===================+============+
| another_missing   | index      |
+-------------------+------------+
| missing_section   | index      |
+-------------------+------------+

Glossary terms (term)
---------------------

+-------------------+------------+
| Label             | Used In    |
+===================+============+
| missing_term      | index      |
+-------------------+------------+
```

## Usage

Add `hermesbaby.partly` to your Sphinx `extensions` list in `conf.py`:

```python
extensions = [
    'hermesbaby.partly',
    # ... other extensions
]
```

### Configuration

The extension provides several configuration options:

#### `partly_undefined_refs_title`

- **Default**: `'Outgoing Cross-References'`
- **Scope**: `env`
- **Description**: The title of the section that lists undefined references.

```python
partly_undefined_refs_title = 'Unresolved References'
```

#### `partly_inject_bibliography`

- **Default**: `True`
- **Scope**: `env`
- **Description**: Whether to automatically inject a bibliography chapter if no bibliography directive is found and citations are used.

```python
partly_inject_bibliography = False  # Disable bibliography injection
```

## Behavior Details

### What Counts as Undefined

A reference is considered undefined when:

- The target label doesn't exist anywhere in the documentation source
- The reference uses the `:ref:` role with a label that hasn't been defined
- A citation key is referenced but not found in the bibliography

### Citation Handling

Citation references are handled specially:

- Missing bibtex keys are intercepted before Sphinx can raise a warning
- Dummy citation entries are created to allow the build to continue
- Works with `-W` (warnings as errors) without failing
- The `missing-reference` event handler processes both 'std' (cross-references) and 'cite' (citation) domains

### What Doesn't Trigger the Table

The following scenarios do NOT create undefined reference entries:

- **Forward references**: References to labels defined later in the same document
- **Cross-document references**: References to labels in other documents (as long as they exist)
- **Non-`std` domain references**: Only standard domain (`:ref:`) references are tracked

### Build Reporting

At the end of each build, `partly` logs a summary of all undefined references:

```text
The build contains the following unresolved cross-reference(s):
  - missing_section
  - undefined_api
```

This appears in the build log/info output, making it easy to track what needs to be defined.

## Implementation Notes

- The extension uses a custom Sphinx Transform (`CollectPendingXrefs`) that runs before cross-reference resolution to capture all `pending_xref` nodes
- This allows tracking of every reference occurrence, not just unique labels (Sphinx caches resolution per unique label)
- The extension hooks into Sphinx's `missing-reference` event to intercept errors for both:
  - **'std' domain** (cross-references like `:ref:`)
  - **'cite' domain** (citations from sphinx-bibtex or similar)
- **Warning Suppression**: Uses multiple approaches to prevent citation warnings:
  - Adds a logging filter to sphinxcontrib.bibtex logger in `config-inited` event
  - Hooks into `warn-missing-reference` event to suppress warnings before they're emitted
  - Returns reference nodes (instead of None) from `missing-reference` handler
- Dummy entries are registered in the appropriate domain (std labels or cite citations)
- The "Undefined References" section is appended in the `doctree-resolved` event after resolution
- Target anchors are created with IDs matching the undefined label names
- The reference nodes created include proper `refuri` attributes pointing to `#{label_name}`
- Global tracking lists are cleared after each build to prevent accumulation
- Bibliography injection is triggered in `on_build_finished` if citations are detected but no bibliography exists
- The injected bibliography chapter is added to the root document at the top level
- The `config-inited` event is used to capture the root document name for bibliography injection
- Citation detection checks both the cite domain data and document trees for citation_reference nodes

## Version

Current version: 0.2
