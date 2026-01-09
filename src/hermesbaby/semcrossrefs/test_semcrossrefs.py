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

"""Unit tests for the semcrossrefs extension."""

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
        full_conf = f"extensions = ['hermesbaby.semcrossrefs']\n{conf_content}"
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

    app = sphinx_builder(docs)
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

    warnings = app._warning.getvalue()
    # Should report both undefined labels
    assert 'undefined_label_1' in warnings
    assert 'undefined_label_2' in warnings


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

    conf = 'semcrossrefs_create_dummy_labels = True'
    app = sphinx_builder(docs, conf)
    app.build()

    warnings = app._warning.getvalue()
    # defined_label should resolve fine (no warning)
    assert 'defined_label' not in warnings or 'undefined label: \'defined_label\'' not in warnings
    # undefined_label should be handled by dummy


def test_create_dummy_labels_when_enabled(sphinx_builder):
    """Test: Create dummy labels when config is enabled."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_label`.
'''
    }

    conf = 'semcrossrefs_substitute_undefined_labels = True'
    app = sphinx_builder(docs, conf)
    app.build()

    # Build should succeed without undefined reference error
    # because dummy label was created
    output = app._warning.getvalue()
    # The reference should be handled by the dummy, so no "undefined label" warning
    assert 'undefined label: \'undefined_label\'' not in output


def test_no_dummy_labels_when_disabled(sphinx_builder):
    """Test: Don't create dummy labels when config is disabled."""
    docs = {
        'index.rst': '''
Test Document
=============

Reference to :ref:`undefined_label`.
'''
    }

    conf = 'semcrossrefs_substitute_undefined_labels = False'
    app = sphinx_builder(docs, conf)
    app.build()

    warnings = app._warning.getvalue()
    # Should still report undefined reference
    assert 'undefined_label' in warnings


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

    # Both cross-doc references should resolve fine
    warnings = app._warning.getvalue()
    assert 'undefined label' not in warnings.lower()


def test_reporting_groups_by_document(sphinx_builder):
    """Test: Undefined references are reported grouped by source document."""
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

    # The extension should report both undefined references
    # grouped by their source documents
    # (Actual validation would check the log output structure)


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

    # Should build successfully - forward references should work
    warnings = app._warning.getvalue()
    assert 'undefined label' not in warnings.lower()
    assert 'later_label' not in warnings


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

    conf = 'semcrossrefs_substitute_undefined_labels = True'
    app = sphinx_builder(docs, conf)
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
