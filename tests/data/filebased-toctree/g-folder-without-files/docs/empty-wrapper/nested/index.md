---
orphan: true
---
# Title of empty-wrapper / nested Index

"empty-wrapper" has no files of its own, only this "nested" subfolder. Even
though "nested" itself has real content (this file and "content.md"),
sphinx-etoc's folder walk never descends into a folder that has no files of
its own (see `_assess_folder`/`_doc_item_from_path` in
sphinx_external_toc.tools), so this whole subtree is silently dropped from
the generated _toc.yml. "orphan: true" keeps the build from failing on the
resulting "not included in any toctree" warning.
