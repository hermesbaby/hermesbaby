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

"""Partly extension for Sphinx.

This extension allows building parts of the document.
"""

from sphinx.util import logging

logger = logging.getLogger(__name__)

# Global storage for tracking undefined references during a build
undefined_refs = []


def setup(app):
    """Setup the Sphinx extension."""
    # Connect to events
    app.connect('missing-reference', on_missing_reference)
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_build_finished)

    return {
        'version': '0.2',
        'parallel_read_safe': False,
        'parallel_write_safe': True,
    }


def on_missing_reference(app, env, node, contnode):
    """Handle missing cross-references.

    This event is called when Sphinx cannot resolve a cross-reference.
    We track all missing references and optionally create dummy targets.
    """
    # Extract information about the missing reference
    refdomain = node.get('refdomain', '')
    reftype = node.get('reftype', '')
    reftarget = node.get('reftarget', '')
    refdoc = node.get('refdoc', '')

    # Only process standard domain references
    if refdomain != 'std':
        return None

    # Check if the label actually exists in the environment before treating it as undefined
    # This handles cases where labels are defined after references in the same document
    std_labels = env.domaindata.get('std', {}).get('labels', {})
    std_anonlabels = env.domaindata.get('std', {}).get('anonlabels', {})

    if reftarget in std_labels or reftarget in std_anonlabels:
        # Label exists, this shouldn't be treated as undefined
        # Let Sphinx handle it normally
        logger.debug(f"Label {reftarget} exists in environment, skipping")
        return None

    # Track this undefined reference
    undefined_refs.append({
        'target': reftarget,
        'type': reftype,
        'domain': refdomain,
        'source': refdoc
    })

    # Create dummy label to allow the build to continue
    # Point it to the source document - we'll add the actual target there later
    # in on_doctree_resolved

    # Register in standard domain labels
    env.domaindata['std']['labels'][reftarget] = (
        refdoc,  # Point to the source document
        reftarget,  # The target id
        f'Undefined reference: {reftarget}'
    )
    env.domaindata['std']['anonlabels'][reftarget] = (refdoc, reftarget)
    logger.debug(f"Created dummy label for {reftarget} pointing to {refdoc}")

    # Return a reference node to prevent Sphinx from emitting a warning
    # This allows builds with -W (warningiserror) to succeed
    # We create a reference that will resolve to the target we'll add in on_doctree_resolved
    from docutils import nodes

    # Create a reference node that points to the label we just registered
    refnode = nodes.reference('', '', internal=True)
    refnode['refuri'] = f'#{reftarget}'
    refnode['reftitle'] = f'Undefined reference: {reftarget}'
    refnode += contnode

    return refnode


def on_doctree_resolved(app, doctree, docname):
    """Add a section listing undefined references at the end of each document.

    This is called after cross-reference resolution for each document.
    """
    from docutils import nodes

    # Find all undefined references in this document
    doc_undefined_refs = [ref for ref in undefined_refs if ref['source'] == docname]

    if not doc_undefined_refs:
        # No undefined references in this document
        return

    # Get unique labels for this document
    unique_labels = sorted(set(ref['target'] for ref in doc_undefined_refs))

    # Create a new section for undefined references
    section = nodes.section(ids=['undefined-references'])
    section += nodes.title('', 'Undefined References')

    # Add a paragraph explaining what this section is
    para = nodes.paragraph()
    para += nodes.Text('The following cross-references could not be resolved:')
    section += para

    # Create a table with the undefined labels
    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    table += tgroup

    # Define column widths
    tgroup += nodes.colspec(colwidth=1)
    tgroup += nodes.colspec(colwidth=1)

    # Table header
    thead = nodes.thead()
    tgroup += thead
    row = nodes.row()
    thead += row
    entry = nodes.entry()
    entry += nodes.paragraph('', 'Label')
    row += entry
    entry = nodes.entry()
    entry += nodes.paragraph('', 'Referenced From')
    row += entry

    # Table body with labels
    tbody = nodes.tbody()
    tgroup += tbody
    for label in unique_labels:
        row = nodes.row()
        tbody += row

        # Label column - add a target here so references can point to it
        entry = nodes.entry()

        # Create a target node for this label
        target = nodes.target('', '', ids=[label], names=[label])
        entry += target

        # Add the label text
        entry += nodes.paragraph('', label)
        row += entry

        # Referenced from column
        refs_from = sorted(set(ref['source'] for ref in doc_undefined_refs if ref['target'] == label))
        entry = nodes.entry()
        entry += nodes.paragraph('', ', '.join(refs_from))
        row += entry

    section += table

    # Append the section to the document
    doctree += section

def on_build_finished(app, exception):
    """Report undefined references at the end of the build."""
    if undefined_refs:
        # Get unique labels
        unique_labels = sorted(set(ref['target'] for ref in undefined_refs))
        logger.info("The build contains the following unresolved cross-reference(s):")
        for label in unique_labels:
            logger.info(f"  - {label}")

    # Clear for next build
    undefined_refs.clear()
