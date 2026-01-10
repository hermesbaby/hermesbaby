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

from docutils import nodes
from docutils.transforms import Transform
from sphinx import addnodes
from sphinx.util import logging
from sphinx.transforms import SphinxTransform

logger = logging.getLogger(__name__)

# Global storage for tracking undefined references during a build
undefined_refs = []
# Storage for tracking all pending_xref nodes before resolution
pending_xrefs = []


class CollectPendingXrefs(SphinxTransform):
    """Transform to collect pending cross-references before resolution.

    This runs early in the transform pipeline to capture all pending_xref nodes
    before Sphinx resolves them. This allows us to count all reference occurrences,
    not just unique targets.
    """
    # Run before ReferencesResolver (priority 10)
    default_priority = 5

    def apply(self):
        """Collect all pending_xref nodes in this document."""
        for node in self.document.findall(addnodes.pending_xref):
            if node.get('refdomain') == 'std':
                pending_xrefs.append({
                    'target': node.get('reftarget', ''),
                    'type': node.get('reftype', ''),
                    'domain': node.get('refdomain', ''),
                    'source': self.env.docname,
                    'line': node.line
                })
                logger.debug(f"Collected pending_xref: {node.get('reftarget')} at line {node.line}")


def setup(app):
    """Setup the Sphinx extension."""
    # Register transform to collect pending xrefs before resolution
    app.add_transform(CollectPendingXrefs)

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

    # Get the set of undefined labels (those that had on_missing_reference called)
    undefined_label_set = {ref['target'] for ref in undefined_refs}

    # Filter pending_xrefs to find all occurrences in this document that are actually undefined
    ref_occurrences = [
        ref for ref in pending_xrefs
        if ref['source'] == docname and ref['target'] in undefined_label_set
    ]

    if not ref_occurrences:
        return

    # Sort by label for better visual grouping
    ref_occurrences_sorted = sorted(ref_occurrences, key=lambda r: r['target'])

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
    entry += nodes.paragraph('', 'Document')
    row += entry

    # Table body - one row per reference occurrence
    tbody = nodes.tbody()
    tgroup += tbody

    # Track which labels we've already created targets for
    targets_created = set()

    for ref in ref_occurrences_sorted:
        label = ref['target']
        source = ref['source']

        row = nodes.row()
        tbody += row

        # Label column
        entry = nodes.entry()

        # Create a target node for this label only once (first occurrence)
        if label not in targets_created:
            target = nodes.target('', '', ids=[label], names=[label])
            entry += target
            targets_created.add(label)

        # Add the label text
        entry += nodes.paragraph('', label)
        row += entry

        # Document column (where this specific reference occurs)
        entry = nodes.entry()
        entry += nodes.paragraph('', source)
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
    pending_xrefs.clear()
