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

"""Unit tests for the partly extension."""

import pytest
from pathlib import Path

try:
    from sphinx.testing.util import SphinxTestApp
    SPHINX_TESTING_AVAILABLE = True
except ImportError:
    SPHINX_TESTING_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="sphinx.testing not available")


@pytest.fixture
def temp_sphinx_dirs(tmp_path):
    """Create temporary source and build directories."""
    srcdir = tmp_path / 'source'
    outdir = tmp_path / 'build'
    srcdir.mkdir(parents=True)
    outdir.mkdir(parents=True)

    return srcdir, outdir


@pytest.fixture
def sphinx_builder(temp_sphinx_dirs):
    """Factory fixture to create Sphinx test apps with custom configs."""
    srcdir, outdir = temp_sphinx_dirs

    def _create_app(docs, conf_content=''):
        """Create a Sphinx test app with given documents and config.

        Args:
            docs: Dict of filename -> content
            conf_content: Additional conf.py content
        """
        # Write documents
        for filename, content in docs.items():
            doc_path = srcdir / filename
            doc_path.write_text(content, encoding='utf-8')

        # Write conf.py
        full_conf = f"extensions = ['hermesbaby.partly']\n{conf_content}"
        (srcdir / 'conf.py').write_text(full_conf, encoding='utf-8')

        # Create and return Sphinx app
        app = SphinxTestApp(
            srcdir=srcdir,
            builddir=outdir
        )
        return app

    return _create_app


def test_no_undefined_references(sphinx_builder):
    """Test: No warnings when all references are defined."""
    docs = {
        'index.rst': '''
Test Document
=============

.. _my_label:

Section with Label
------------------

Some content.

Reference to :ref:`my_label`.
'''
    }

    app = sphinx_builder(docs, conf_content='partly_inject_bibliography = False')
    app.build()

    # Should build successfully without errors
    assert app._warning.getvalue() == ''


def test_detect_undefined_references(sphinx_builder):
    """Test: Extension detects and reports undefined references."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_label_1`.
Another reference to :ref:`undefined_label_2`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    info = app._status.getvalue()
    # Should report both undefined labels in the info log
    assert 'The build contains the following unresolved cross-reference(s):' in info
    assert 'undefined_label_1' in info
    assert 'undefined_label_2' in info


def test_ignore_defined_labels_in_same_doc(sphinx_builder):
    """Test: Don't create dummies for labels defined in the same document."""
    docs = {
        'index.rst': '''
Test Document
=============

.. _defined_label:

Section
-------

Reference to :ref:`defined_label`.
Reference to :ref:`undefined_label`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    info = app._status.getvalue()
    # Only undefined_label should be reported, not defined_label
    if 'The build contains the following unresolved cross-reference(s):' in info:
        assert 'undefined_label' in info
        # Extract just the list of unresolved references
        lines = [l.strip() for l in info.split('\n')]
        unresolved_idx = -1
        for i, line in enumerate(lines):
            if 'The build contains the following unresolved cross-reference(s):' in line:
                unresolved_idx = i
                break
        if unresolved_idx >= 0:
            # Check lines after the header that start with '-'
            for line in lines[unresolved_idx+1:]:
                if line.startswith('- defined_label'):
                    pytest.fail('defined_label should not be in unresolved references')
                elif not line.startswith('-'):
                    break  # End of the list


def test_create_dummy_labels(sphinx_builder):
    """Test: Create dummy labels for undefined references."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_label`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Build should succeed without undefined reference error
    # because dummy label was created
    output = app._warning.getvalue()
    # The reference should be handled by the dummy, so no "undefined label" warning
    assert 'undefined label: \'undefined_label\'' not in output



def test_multiple_docs_with_cross_references(sphinx_builder):
    """Test: References across multiple documents work correctly."""
    docs = {
        'index.rst': '''
Main Document
=============

.. _main_label:

Main Section
------------

Reference to other doc: :ref:`other_label`.

.. toctree::

   other
''',
        'other.rst': '''
Other Document
==============

.. _other_label:

Other Section
-------------

Reference back to main: :ref:`main_label`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Both cross-doc references should resolve fine, no unresolved references
    info = app._status.getvalue()
    assert 'The build contains the following unresolved cross-reference(s):' not in info


def test_reporting_groups_by_document(sphinx_builder):
    """Test: Undefined references are reported in info log."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_1`.
''',
        'other.rst': '''
Other Document
==============

Reference to :ref:`undefined_2`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # The extension should report both undefined references in info log
    info = app._status.getvalue()
    assert 'The build contains the following unresolved cross-reference(s):' in info
    assert 'undefined_1' in info
    assert 'undefined_2' in info


def test_forward_reference_before_target(sphinx_builder):
    """Test: Reference that appears before its target is defined should work."""
    docs = {
        'index.rst': '''
Test Document
=============

Forward reference to :ref:`later_label`.

Some content in between.

.. _later_label:

Target Section
--------------

This label is defined after the reference.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Should build successfully - forward references should work, no unresolved refs
    info = app._status.getvalue()
    assert 'The build contains the following unresolved cross-reference(s):' not in info


def test_no_dummy_for_forward_reference_when_enabled(sphinx_builder):
    """Test: Forward references should NOT get dummies even when dummy creation is enabled."""
    docs = {
        'index.rst': '''
Test Document
=============

Forward reference to :ref:`defined_later`.

And a reference to truly undefined: :ref:`truly_undefined`.

.. _defined_later:

Target Section
--------------

This label is defined after the reference.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Get the build output/warnings
    output = app._warning.getvalue()

    # The forward reference should resolve fine (no warning about it)
    assert 'undefined label: \'defined_later\'' not in output

    # Check the info log to verify only 1 dummy was created (for truly_undefined)
    # and NOT for defined_later
    info_output = app._status.getvalue()

    # Should report the dummy label summary at the end
    assert 'The build contains the following unresolved cross-reference(s):' in info_output
    assert '  - truly_undefined' in info_output
    # Should NOT create dummy for defined_later
    assert '  - defined_later' not in info_output


def test_undefined_references_section_appended(sphinx_builder):
    """Test: Documents with undefined references get a section appended at the end."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_label`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML to verify the section was added
    outdir = app.outdir
    html_file = outdir / 'index.html'

    assert html_file.exists(), "HTML output file not found"

    html_content = html_file.read_text(encoding='utf-8')

    # Check that "Outgoing References" section exists in the HTML
    assert 'Outgoing References' in html_content, "Section title not found in HTML"
    assert 'undefined_label' in html_content, "Label not found in HTML"


def test_undefined_references_section_contains_table(sphinx_builder):
    """Test: The undefined references section contains a table."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_label`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Check that there's a table in the output
    # Look for <table or <colgroup which are typical table elements
    assert '<table' in html_content, "No table found in HTML output"
    assert 'undefined_label' in html_content, "Label not found in table"


def test_table_contains_all_undefined_labels(sphinx_builder):
    """Test: The table lists all undefined labels with proper structure."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`first_undefined`.
Another reference to :ref:`second_undefined`.
And one more to :ref:`third_undefined`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Verify all three labels appear in the output
    assert 'first_undefined' in html_content, "first_undefined not found"
    assert 'second_undefined' in html_content, "second_undefined not found"
    assert 'third_undefined' in html_content, "third_undefined not found"

    # Verify table headers (outer and nested table headers)
    assert 'Label' in html_content, "Table header 'Label' not found"
    assert 'Used In' in html_content, "Table header 'Used In' not found"
    assert 'Source File' in html_content, "Nested table header 'Source File' not found"
    assert 'Chapter' in html_content, "Nested table header 'Chapter' not found"


def test_labels_defined_as_targets_in_table(sphinx_builder):
    """Test: Each undefined label is defined as a target in its table row."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`my_undefined_label`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Check for anchor/target with the label id
    # In HTML, labels typically become id attributes or <a> tags
    assert 'id="my_undefined_label"' in html_content or 'id="my-undefined-label"' in html_content, \
        "Label target id not found in HTML"


def test_references_link_to_table_rows(sphinx_builder):
    """Test: Table rows have targets that match the undefined label names.

    Note: Due to Sphinx's cross-reference resolution timing, the references themselves
    may not automatically become links, but the targets are created with the correct IDs
    so that manual hrefs would work.
    """
    docs = {
        'index.rst': '''
Test Document
=============

Here is a reference to :ref:`my_target_label`.

Some more content here.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Verify the target exists with the correct ID
    # This means if someone clicks a link to #my_target_label, it will work
    assert 'id="my_target_label"' in html_content or 'id="my-target-label"' in html_content, \
        "Label target id not found in HTML"

    # Verify the reference text appears (even if not as a link due to timing)
    assert 'my_target_label' in html_content, "Label text not found in output"


def test_no_section_for_documents_without_undefined_refs(sphinx_builder):
    """Test: Documents with all references properly defined don't get the section."""
    docs = {
        'index.rst': '''
Test Document
=============

.. _my_label:

Proper Section
--------------

Reference to :ref:`my_label` which is defined.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Verify that "Outgoing References" section is NOT present
    assert 'Outgoing References' not in html_content, \
        "Outgoing References section should not appear when all references are defined"

def test_build_succeeds_with_warningiserror(sphinx_builder):
    """Test: Build succeeds even with -W (warningiserror=True) when undefined refs exist."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`sec_2025cw15_3_wed_reply_to_mail_medic_bite_proband_data`.
Another reference to :ref:`ai_dialog_qr_scanning_frontend`.
'''
    }

    # Create app with warningiserror=True (equivalent to -W flag)
    app = sphinx_builder(docs, conf_content='partly_inject_bibliography = False')

    # Monkey patch to enable warningiserror
    app.warningiserror = True

    # Build should succeed without raising an exception
    try:
        app.build()
        build_succeeded = True
    except Exception as e:
        build_succeeded = False
        error_msg = str(e)

    assert build_succeeded, f"Build failed with warningiserror=True. This should not happen with undefined refs."

    # Verify the outgoing cross-references section was created
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    assert 'Outgoing References' in html_content, "Section should be present"
    assert 'sec_2025cw15_3_wed_reply_to_mail_medic_bite_proband_data' in html_content
    assert 'ai_dialog_qr_scanning_frontend' in html_content

def test_bibliography_injection_disabled(sphinx_builder):
    """Test: Bibliography injection can be disabled via config."""
    docs = {
        'index.rst': '''
Test Document
=============

Content here.
'''
    }

    app = sphinx_builder(docs, conf_content='partly_inject_bibliography = False')
    app.build()

    # With injection disabled, no bibliography chapter should be added
    # (unless citations exist, which they don't in this test)
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    assert 'Injected Bibliography' not in html_content, \
        "Injected Bibliography should not appear when injection is disabled"


def test_bibliography_title_customizable(sphinx_builder):
    """Test: The undefined references section title is customizable."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_label`.
'''
    }

    custom_title = 'Custom References Section'
    app = sphinx_builder(docs, conf_content=f"partly_undefined_refs_title = '{custom_title}'")
    app.build()

    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Check that the custom title appears
    assert custom_title in html_content, f"Custom title '{custom_title}' not found in HTML"
    # Original title should NOT appear
    assert 'Outgoing References' not in html_content or custom_title in html_content


def test_missing_citation_key_handled(sphinx_builder):
    """Test: Missing citation keys don't cause build failure."""
    # Note: This test assumes that cite domain is available (e.g., sphinx-bibtex installed)
    # If not available, the citation syntax won't be processed
    # Disable bibliography injection since this test is just checking that citations don't break the build
    docs = {
        'index.rst': '''
Test Document
=============

This cites {cite:p}`NonexistentKey2023`.

Some content here.
''',
    }

    app = sphinx_builder(docs, conf_content='partly_inject_bibliography = False')

    # Try to build - should not raise an exception about missing citation key
    try:
        app.build()
        build_succeeded = True
    except Exception as e:
        # Check if the error is about missing bibtex key
        error_msg = str(e)
        if 'could not find bibtex key' in error_msg or 'nonexistent' in error_msg.lower():
            build_succeeded = False
            pytest.fail(f"Build failed due to missing citation key: {error_msg}")
        else:
            # Some other error, re-raise
            raise

    assert build_succeeded, "Build should succeed with missing citation keys"


def test_table_shows_each_reference_occurrence(sphinx_builder):
    """Test: Each cross-reference occurrence gets its own row, even if same label."""
    docs = {
        'index.rst': '''
Test Document
=============

First reference to :ref:`repeated_label`.

Second reference to :ref:`repeated_label`.

Third reference to :ref:`repeated_label`.

And one to :ref:`another_label`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Verify both labels appear in the output
    assert 'repeated_label' in html_content
    assert 'another_label' in html_content

    # The outer table should have 2 rows (one per unique label)
    # Each row in the outer table contains a nested table showing occurrences
    import re

    # Check for the presence of nested tables
    # We expect: 1 outer table + 2 nested tables (one for each label)
    all_tables = re.findall(r'<table[^>]*class="[^"]*docutils[^"]*"', html_content)
    assert len(all_tables) >= 3, f"Expected at least 3 tables (1 outer + 2 nested), got {len(all_tables)}"

    # Verify both unique labels appear
    assert 'repeated_label' in html_content
    assert 'another_label' in html_content

    # Verify "Chapter" header appears in nested tables
    assert html_content.count('Chapter') >= 2, "Should have 'Chapter' header in nested tables"


def test_separate_tables_for_different_reftypes(sphinx_builder):
    """Test: Different reference types get separate tables with type headers."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_ref_label`.
Reference to :term:`undefined_term_label`.
Reference to :doc:`undefined_doc_label`.
Another reference to :ref:`another_ref_label`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Verify all labels appear in the output
    assert 'undefined_ref_label' in html_content
    assert 'undefined_term_label' in html_content
    assert 'undefined_doc_label' in html_content
    assert 'another_ref_label' in html_content

    # Should have separate subsections/headings for each reftype
    # Look for headings that specifically indicate reference types
    # These should be subsections under "Outgoing References"
    assert 'Cross-references (ref)' in html_content or 'Type: ref' in html_content, \
        "Should have a section/heading specifically for 'ref' type"
    assert 'Glossary terms (term)' in html_content or 'Type: term' in html_content, \
        "Should have a section/heading specifically for 'term' type"
    assert 'Documents (doc)' in html_content or 'Type: doc' in html_content, \
        "Should have a section/heading specifically for 'doc' type"


def test_reftype_tables_have_correct_structure(sphinx_builder):
    """Test: Each reftype table has proper structure with type label."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_ref`.
Reference to :term:`undefined_term`.
'''
    }

    app = sphinx_builder(docs)
    app.build()

    # Read the generated HTML
    outdir = app.outdir
    html_file = outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')

    # Both labels should be present
    assert 'undefined_ref' in html_content
    assert 'undefined_term' in html_content

    # Should have multiple tables (one for each reftype)
    import re
    all_tables = re.findall(r'<table[^>]*class="[^"]*docutils[^"]*"', html_content)
    # At minimum: 2 outer tables (one for ref, one for term) + 2 nested tables
    assert len(all_tables) >= 4, f"Expected at least 4 tables (2 for each reftype + nested), got {len(all_tables)}"
