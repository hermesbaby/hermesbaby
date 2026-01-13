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
# Track if bibliography directive exists in any document
has_bibliography_directive = False
# Track root document name for injecting bibliography if needed
root_docname = None
# Track if we need to inject bibliography
should_inject_bibliography = False


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
        from docutils import nodes
        for node in self.document.findall(addnodes.pending_xref):
            if node.get('refdomain') == 'std':
                # Find the parent section of this reference
                section_id = None
                section_title = None
                parent = node.parent
                while parent:
                    if isinstance(parent, nodes.section):
                        # Get the section ID
                        if parent.get('ids'):
                            section_id = parent['ids'][0]
                        # Get the section title
                        title_nodes = [n for n in parent.children if isinstance(n, nodes.title)]
                        if title_nodes:
                            section_title = title_nodes[0].astext()
                        break
                    parent = parent.parent

                pending_xrefs.append({
                    'target': node.get('reftarget', ''),
                    'type': node.get('reftype', ''),
                    'domain': node.get('refdomain', ''),
                    'source': self.env.docname,
                    'line': node.line,
                    'section_id': section_id,
                    'section_title': section_title or 'Top of document'
                })
                logger.debug(f"Collected pending_xref: {node.get('reftarget')} at line {node.line} in section {section_title}")


def setup(app):
    """Setup the Sphinx extension."""
    # Add configuration value for the section title
    app.add_config_value('partly_undefined_refs_title', 'Outgoing References', 'env')
    app.add_config_value('partly_inject_bibliography', True, 'env')

    # Register transform to collect pending xrefs before resolution
    app.add_transform(CollectPendingXrefs)

    # Connect to events
    app.connect('config-inited', on_config_inited)
    app.connect('env-before-read-docs', on_env_before_read_docs)
    app.connect('source-read', on_source_read)
    app.connect('missing-reference', on_missing_reference)
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_build_finished)

    return {
        'version': '0.2',
        'parallel_read_safe': False,
        'parallel_write_safe': True,
    }


def on_env_before_read_docs(app, env, docnames):
    """Check for bibliography directive before reading documents.

    This scans all documents to determine if a bibliography directive exists.
    """
    global has_bibliography_directive

    # Reset for this build
    has_bibliography_directive = False

    import os

    # Quick scan for bibliography directive in source files
    for docname in docnames:
        try:
            docpath = env.doc2path(docname)
            if os.path.exists(docpath):
                with open(docpath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for bibliography directive
                if '.. bibliography::' in content or '```{bibliography}' in content:
                    has_bibliography_directive = True
                    logger.debug(f"Found bibliography directive in {docname}")
                    break
        except Exception as e:
            logger.debug(f"Error scanning {docname}: {e}")





def on_source_read(app, docname, source):
    """Inject bibliography directive into root document source if missing.

    This modifies the in-memory source BEFORE parsing, allowing sphinxcontrib-bibtex
    to properly process the bibliography directive.
    """
    global has_bibliography_directive, root_docname

    # Only process the root document
    if docname != root_docname:
        return

    # If bibliography already exists or injection is disabled, skip
    if has_bibliography_directive or not app.config.partly_inject_bibliography:
        return

    # Determine format based on file extension
    try:
        source_path = app.env.doc2path(docname, base=False)
        is_markdown = source_path.endswith('.md')
    except Exception:
        is_markdown = False

    # Inject bibliography directive at the end of the source
    if is_markdown:
        bibliography_directive = "\n\n```{bibliography}\n```\n"
    else:
        bibliography_directive = "\n\n.. bibliography::\n"

    # Modify the source in-memory (source is a list with one string element)
    source[0] = source[0] + bibliography_directive
    has_bibliography_directive = True
    logger.info(f"Injected bibliography directive into {docname}")


def on_config_inited(app, config):
    """Initialize tracking variables when config is initialized."""
    global root_docname
    root_docname = app.config.master_doc

    # Suppress bibtex citation warnings at the Sphinx application level
    # This is the most direct way to prevent "could not find bibtex key" errors
    if not hasattr(app.config, 'suppress_warnings'):
        app.config.suppress_warnings = []

    # Add bibtex warnings to the suppression list
    if 'app.add_node' not in app.config.suppress_warnings:
        app.config.suppress_warnings.append('app.add_node')
    if 'bibtex' not in app.config.suppress_warnings:
        app.config.suppress_warnings.append('bibtex')
    if 'cite' not in app.config.suppress_warnings:
        app.config.suppress_warnings.append('cite')

    logger.info("Added bibtex warnings to suppress_warnings config")

    # Patch Sphinx's warning system to filter bibtex warnings
    # sphinxcontrib-bibtex uses env.warn_node or logger.warning
    if hasattr(app, 'env') and hasattr(app.env, 'warn_node'):
        original_warn_node = app.env.warn_node

        def filtered_warn_node(msg, node, **kwargs):
            """Filter out bibtex citation warnings."""
            msg_str = str(msg).lower()
            if 'could not find bibtex key' in msg_str or 'bibtex key' in msg_str:
                logger.debug(f"Suppressed bibtex warning via warn_node: {msg}")
                return
            return original_warn_node(msg, node, **kwargs)

        app.env.warn_node = filtered_warn_node
        logger.info("Patched env.warn_node to filter bibtex warnings")

    # Patch app.warn for older Sphinx versions (removed in Sphinx 2.0+)
    if hasattr(app, 'warn'):
        original_warn = app.warn

        def filtered_warn(message, *args, **kwargs):
            """Filter out bibtex citation warnings."""
            msg_str = str(message).lower()
            if 'could not find bibtex key' in msg_str or 'bibtex key' in msg_str:
                logger.debug(f"Suppressed bibtex warning via app.warn: {message}")
                return
            return original_warn(message, *args, **kwargs)

        app.warn = filtered_warn
        logger.info("Patched app.warn to filter bibtex warnings")

    # For newer Sphinx versions, patch the StatusCode logger
    try:
        import sphinx.util.logging as sphinx_logging
        # Get the logger that sphinx uses for warnings
        sphinx_logger = sphinx_logging.getLogger(__name__)

        # Add filter to catch bibtex warnings
        class BibtexWarningFilter(python_logging.Filter):
            def filter(self, record):
                msg = record.getMessage().lower()
                if 'could not find bibtex key' in msg or 'bibtex key' in msg:
                    logger.debug(f"Suppressed bibtex warning via logging: {record.getMessage()}")
                    return False
                return True

        sphinx_logger.addFilter(BibtexWarningFilter())
        logger.info("Added filter to Sphinx logger")
    except Exception as e:
        logger.debug(f"Could not add Sphinx logger filter: {e}")

    # Suppress specific warnings from sphinxcontrib-bibtex logger
    try:
        import logging as python_logging
        bibtex_logger = python_logging.getLogger('sphinxcontrib.bibtex')
        if bibtex_logger:
            class CitationWarningFilter(python_logging.Filter):
                def filter(self, record):
                    msg = record.getMessage().lower()
                    if 'could not find bibtex key' in msg or ('citation' in msg and 'not found' in msg):
                        logger.debug(f"Suppressed citation warning: {record.getMessage()}")
                        return False
                    return True
            bibtex_logger.addFilter(CitationWarningFilter())
            logger.debug("Added citation warning filter to sphinxcontrib.bibtex logger")
    except Exception as e:
        logger.debug(f"Could not add citation warning filter: {e}")


def on_missing_reference(app, env, node, contnode):
    """Handle missing cross-references and citations.

    This event is called when Sphinx cannot resolve a cross-reference.
    We track all missing references and optionally create dummy targets.
    Handles both 'std' domain (cross-references) and 'cite' domain (citations).
    """
    # Extract information about the missing reference
    refdomain = node.get('refdomain', '')
    reftype = node.get('reftype', '')
    reftarget = node.get('reftarget', '')
    refdoc = node.get('refdoc', '')

    # Handle standard domain references (cross-references)
    if refdomain == 'std':
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
            reftarget  # Just use the label name
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
        refnode['reftitle'] = reftarget  # Just use the label name
        refnode += contnode

        return refnode

    # Handle citation references (cite domain)
    elif refdomain == 'cite':
        logger.debug(f"Missing citation key: {reftarget} in {refdoc}")

        # Create a dummy citation entry to prevent warning
        # This allows the build to continue and the bibliography will be injected later
        cite_domain = env.domaindata.get('cite', {})

        # Ensure the cite domain data structure exists
        if 'cite' not in env.domaindata:
            env.domaindata['cite'] = {
                'citations': {},
                'citation_refs': {}
            }

        # Register dummy citation
        env.domaindata['cite']['citations'][reftarget] = {
            'docname': refdoc,
            'target': reftarget
        }
        logger.debug(f"Created dummy citation entry for {reftarget}")

        # Return a reference node that looks like a citation reference
        from docutils import nodes as docnodes
        from sphinx.domains.citations import CitationReference

        # Create a citation reference node
        refnode = docnodes.reference('', '', internal=True)
        refnode['refuri'] = f'#{reftarget}'
        refnode += contnode

        return refnode

    # Return None for other domains (let Sphinx handle them)
    return None


def on_warn_missing_reference(app, domain, node):
    """Suppress warnings for missing citations.

    This event is called before Sphinx emits a warning about a missing reference.
    Return True to suppress the warning.
    """
    # Check if this is a citation warning
    if domain == 'cite' or (hasattr(node, 'get') and node.get('refdomain') == 'cite'):
        reftarget = node.get('reftarget', '') if hasattr(node, 'get') else ''
        logger.debug(f"Suppressing citation warning for: {reftarget}")
        return True  # Suppress the warning

    return False  # Don't suppress other warnings


def on_doctree_resolved(app, doctree, docname):
    """Add a section listing undefined references at the end of each document.

    This is called after cross-reference resolution for each document.
    Also checks for bibliography directive and tracks citation references.
    """
    from docutils import nodes

    # Check if this document has a bibliography directive
    global has_bibliography_directive, should_inject_bibliography
    if not has_bibliography_directive:
        # Search for bibliography directive
        for node_obj in doctree.traverse():
            if (isinstance(node_obj, addnodes.productionlist) or
                (isinstance(node_obj, nodes.Element) and
                 node_obj.tagname == 'directive' and
                 node_obj.get('name') == 'bibliography')):
                has_bibliography_directive = True
                logger.debug(f"Found bibliography directive in {docname}")
                break
            # Also check for literal block markers that might indicate bibliography
            if hasattr(node_obj, 'tagname') and node_obj.tagname == 'citation':
                has_bibliography_directive = True
                logger.debug(f"Found citation element in {docname}")
                break

    # Handle outgoing cross-references (existing functionality)
    # Get the set of undefined labels (those that had on_missing_reference called)
    undefined_label_set = {ref['target'] for ref in undefined_refs}

    # Filter pending_xrefs to find all occurrences in this document that are actually undefined
    ref_occurrences = [
        ref for ref in pending_xrefs
        if ref['source'] == docname and ref['target'] in undefined_label_set
    ]

    if ref_occurrences:
        # Sort by reftype first, then by label for better visual grouping
        ref_occurrences_sorted = sorted(ref_occurrences, key=lambda r: (r['type'], r['target']))

        # Group occurrences by reftype first
        from itertools import groupby
        grouped_by_type = {reftype: list(group) for reftype, group in groupby(ref_occurrences_sorted, key=lambda r: r['type'])}

        # Create a new section for outgoing cross-references
        # Use configurable title
        section_title = app.config.partly_undefined_refs_title
        section = nodes.section(ids=['outgoing-cross-references'])
        section += nodes.title('', section_title)

        # Define friendly names for reference types
        reftype_names = {
            'ref': 'Cross-references (ref)',
            'term': 'Glossary terms (term)',
            'doc': 'Documents (doc)',
            'numref': 'Numbered references (numref)',
            'keyword': 'Keywords (keyword)',
            'option': 'Options (option)',
            'envvar': 'Environment variables (envvar)',
        }

        # Create a subsection for each reftype
        for reftype, refs_of_type in grouped_by_type.items():
            # Get friendly name or use the type itself
            subsection_title = reftype_names.get(reftype, f'Type: {reftype}')

            # Create subsection
            subsection = nodes.section(ids=[f'outgoing-cross-references-{reftype}'])
            subsection += nodes.title('', subsection_title)

            # Group occurrences by label within this reftype
            grouped_refs = {label: list(group) for label, group in groupby(refs_of_type, key=lambda r: r['target'])}

            # Create outer table with 2 columns: Label and Used In
            table = nodes.table()
            tgroup = nodes.tgroup(cols=2)
            table += tgroup

            # Define column widths
            tgroup += nodes.colspec(colwidth=1)
            tgroup += nodes.colspec(colwidth=3)

            # Table header
            thead = nodes.thead()
            tgroup += thead
            row = nodes.row()
            thead += row
            entry = nodes.entry()
            entry += nodes.paragraph('', 'Label')
            row += entry
            entry = nodes.entry()
            entry += nodes.paragraph('', 'Used In')
            row += entry

            # Table body - one row per unique label
            tbody = nodes.tbody()
            tgroup += tbody

            for label, occurrences in grouped_refs.items():
                row = nodes.row()
                tbody += row

                # Label column
                entry = nodes.entry()
                # Create a target node for this label
                target = nodes.target('', '', ids=[label], names=[label])
                entry += target
                # Add the label text in verbatim/code font
                para = nodes.paragraph()
                para += nodes.literal('', label)
                entry += para
                row += entry

                # Used In column - contains nested table
                entry = nodes.entry()

                # Create nested table
                nested_table = nodes.table()
                nested_tgroup = nodes.tgroup(cols=2)
                nested_table += nested_tgroup

                # Nested table column widths
                nested_tgroup += nodes.colspec(colwidth=2)
                nested_tgroup += nodes.colspec(colwidth=1)

                # Nested table header
                nested_thead = nodes.thead()
                nested_tgroup += nested_thead
                nested_row = nodes.row()
                nested_thead += nested_row
                nested_entry = nodes.entry()
                nested_entry += nodes.paragraph('', 'Chapter')
                nested_row += nested_entry
                nested_entry = nodes.entry()
                nested_entry += nodes.paragraph('', 'Source File')
                nested_row += nested_entry

                # Nested table body - one row per occurrence
                nested_tbody = nodes.tbody()
                nested_tgroup += nested_tbody

                for ref in occurrences:
                    source = ref['source']
                    section_id = ref.get('section_id')
                    section_title = ref.get('section_title', 'Top of document')

                    nested_row = nodes.row()
                    nested_tbody += nested_row

                    # Chapter column
                    nested_entry = nodes.entry()
                    nested_para = nodes.paragraph()
                    if section_id:
                        # Create a reference to the section
                        refnode = nodes.reference('', '', internal=True)
                        refnode['refuri'] = f'#{section_id}'
                        refnode += nodes.Text(section_title)
                        nested_para += refnode
                    else:
                        # No section ID, just show the title as text
                        nested_para += nodes.Text(section_title)
                    nested_entry += nested_para
                    nested_row += nested_entry

                    # Source File column
                    nested_entry = nodes.entry()
                    nested_para = nodes.paragraph()
                    # Add file suffix to source file name
                    source_with_suffix = app.env.doc2path(source, base=False)
                    nested_para += nodes.literal('', source_with_suffix)
                    nested_entry += nested_para
                    nested_row += nested_entry

                entry += nested_table
                row += entry

            subsection += table
            section += subsection

        # Append the section to the document
        doctree += section

    # Inject bibliography directive if needed and this is the root document
    # Check if we should inject based on current state (not waiting for build_finished)
    if (docname == root_docname and
        not has_bibliography_directive and
        app.config.partly_inject_bibliography):
        # Check if there are citations that need a bibliography
        if _has_citation_references(app):
            logger.info("Injecting bibliography into root document")
            _inject_bibliography_chapter(app, doctree)
            has_bibliography_directive = True  # Mark as injected

def on_build_finished(app, exception):
    """Report undefined references at the end of the build and determine if bibliography is needed."""
    global undefined_refs, pending_xrefs, should_inject_bibliography, has_bibliography_directive

    if undefined_refs:
        # Get unique labels
        unique_labels = sorted(set(ref['target'] for ref in undefined_refs))
        logger.info("The build contains the following unresolved cross-reference(s):")
        for label in unique_labels:
            logger.info(f"  - {label}")

    # Determine if we should inject bibliography
    # This happens if there are pending citations but no bibliography directive
    if not has_bibliography_directive and app.config.partly_inject_bibliography:
        # Check if there are any citation references in the doctree
        # This will be set if we detected pending citations
        if _has_citation_references(app):
            should_inject_bibliography = True
            logger.info("Bibliography directive will be injected (citations detected but no bibliography found)")

    # Clear for next build
    undefined_refs.clear()
    pending_xrefs.clear()
    has_bibliography_directive = False
    should_inject_bibliography = False


def _has_citation_references(app):
    """Check if any document has citation references.

    Returns True if any document contains pending citations or citation references.
    """
    # Check if there are any citation references in the domain data
    try:
        # Check cite domain citations
        cite_domain_data = app.env.domaindata.get('cite', {})
        citations = cite_domain_data.get('citations', {})
        if citations:
            logger.debug(f"Found {len(citations)} citation(s) in domain data")
            return True
    except (AttributeError, KeyError, TypeError):
        pass

    # If cite domain not available or no citations found, check for citation nodes in documents
    try:
        for docname in app.env.found_docs:
            try:
                doctree = app.env.get_doctree(docname)
                # Look for citation references or pending citations
                for node_obj in doctree.traverse():
                    # Check for citation_reference nodes
                    if hasattr(node_obj, 'tagname'):
                        if node_obj.tagname == 'citation_reference':
                            logger.debug(f"Found citation_reference in {docname}")
                            return True
                        # Check for pending xref with cite domain
                        if (node_obj.tagname == 'pending_xref' and
                            node_obj.get('refdomain') == 'cite'):
                            logger.debug(f"Found pending citation in {docname}")
                            return True
                    # Also check class name for citation references
                    if type(node_obj).__name__ == 'citation_reference':
                        logger.debug(f"Found citation_reference node in {docname}")
                        return True
            except Exception as e:
                logger.debug(f"Error checking citations in {docname}: {e}")
    except Exception as e:
        logger.debug(f"Error checking for citation references: {e}")

    return False


def _inject_bibliography_chapter(app, doctree):
    """Inject bibliography directive at the end of the document.

    Appends just the bibliography directive without any wrapper section.
    This allows partial documentation builds with citations to succeed.
    """
    from docutils import nodes as docnodes

    # Create a directive node for the bibliography without any section wrapper
    # Using raw directive to ensure proper RST processing
    # The bibliography directive should be processed by sphinx-bibtex or similar extension
    directive_node = docnodes.raw('', '.. bibliography::', format='rst')

    logger.info("Injected bibliography directive into document")

    # Append the directive directly to the document
    doctree += directive_node
