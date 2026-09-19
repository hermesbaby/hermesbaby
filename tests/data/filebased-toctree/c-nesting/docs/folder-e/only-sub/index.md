---
orphan: true
---
# Title of Folder E / Only-Sub Index

folder-e itself has no files directly inside it, only this subfolder.
sphinx-etoc's create_site_map_from_path requires a folder to contain at
least one file to become a toc entry (see _assess_folder/_doc_item_from_path
in sphinx_external_toc.tools), so folder-e (and everything below it) is
silently dropped from the generated _toc.yml. This fixture documents that
known upstream limitation.
