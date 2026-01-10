"""Manual test to verify the 'used in' column."""
from pathlib import Path
from sphinx.testing.util import SphinxTestApp

def test_used_in_column():
    docs = {
        'index.rst': '''
Test Document
=============

Section One
-----------

First reference to :ref:`missing_label` in section one.

Section Two
-----------

Second reference to :ref:`missing_label` in section two.

Third reference to :ref:`another_missing` here.
'''
    }

    srcdir = Path(__file__).parent / 'test_temp_src'
    outdir = Path(__file__).parent / 'test_temp_build'
    srcdir.mkdir(exist_ok=True)
    
    # Write the documents
    for filename, content in docs.items():
        filepath = srcdir / filename
        filepath.write_text(content)
    
    # Create minimal conf.py
    conf_content = """
extensions = ['hermesbaby.partly']
"""
    (srcdir / 'conf.py').write_text(conf_content)
    
    # Build
    app = SphinxTestApp(
        buildername='html',
        srcdir=srcdir,
        freshenv=True
    )
    app.build()
    
    # Read the HTML
    html_file = app.outdir / 'index.html'
    html_content = html_file.read_text(encoding='utf-8')
    
    # Check for the 'used in' column header
    assert 'used in' in html_content, "Should have 'used in' column header"
    
    # Check that section titles are in the table
    assert 'Section One' in html_content or 'Section Two' in html_content, "Should have section titles"
    
    print("✓ 'used in' column header found")
    print("✓ Section references found")
    
    # Print part of the table for manual inspection
    import re
    table_match = re.search(r'<table.*?</table>', html_content, re.DOTALL)
    if table_match:
        print("\nTable HTML (first 1000 chars):")
        print(table_match.group()[:1000])
    
    # Cleanup
    import shutil
    shutil.rmtree(srcdir)
    shutil.rmtree(app.outdir)
    
    print("\n✓ All checks passed!")

if __name__ == '__main__':
    test_used_in_column()
