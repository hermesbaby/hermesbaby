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

"""Semantic cross-references extension for Sphinx.

This extension:
1. Detects and reports undefined cross-reference labels
2. Optionally creates dummy labels for undefined references to allow builds to complete
"""

from sphinx.util import logging

logger = logging.getLogger(__name__)

# Global storage for tracking undefined references during a build
undefined_refs = []


def setup(app):
    """Setup the Sphinx extension."""
    app.add_config_value('semcrossrefs_substitute_undefined_labels', False, 'env')

    # Connect to events
    app.connect('missing-reference', on_missing_reference)
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

    # If dummy label creation is enabled, create the label now
    if app.config.semcrossrefs_substitute_undefined_labels:
        # Register the dummy label in the environment
        dummy_docname = '_dummy_labels'

        # Register in standard domain labels
        env.domaindata['std']['labels'][reftarget] = (
            dummy_docname,
            reftarget,
            f'Dummy: {reftarget}'
        )
        env.domaindata['std']['anonlabels'][reftarget] = (dummy_docname, reftarget)
        logger.debug(f"Created dummy label: {reftarget}")

        # Return a text node to replace the broken reference
        from docutils import nodes
        return nodes.inline('', f'[{reftarget}]', classes=['dummy-ref'])

    return None


def on_build_finished(app, exception):
    """Report undefined references at the end of the build."""

    if app.config.semcrossrefs_substitute_undefined_labels:
        if undefined_refs:
            # Get unique labels
            unique_labels = sorted(set(ref['target'] for ref in undefined_refs))
            logger.info("The build contains the following unresolved cross-reference(s):")
            for label in unique_labels:
                logger.info(f"  - {label}")

    # Clear for next build
    undefined_refs.clear()
