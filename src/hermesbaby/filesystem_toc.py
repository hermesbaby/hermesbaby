"""Build a _toc.yml from a project's filesystem layout, and merge in the
sphinx-external-toc options declared in Markdown frontmatter.

build_toc_from_filesystem() derives the plain filesystem structure of a
_toc.yml (which file is root, which files/folders are its children, in what
order, ...). It cannot know about the other options sphinx-external-toc
supports (a "title" for a document's toctree entry, or its "options"
mapping: caption, hidden, maxdepth, numbered, reversed, titlesonly, style,
restart_numbering -- see https://github.com/executablebooks/sphinx-external-toc),
since those aren't derivable from the filesystem layout.

Authors declare them instead in a "toctree" frontmatter block of the
corresponding *.md file, e.g.:

    ---
    toctree:
      title: Custom Title
      options:
        hidden: false
        numbered: true
    ---

The rest of this module collects those blocks and merges them into the
generated _toc.yml, in a second pass.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from sphinx.addnodes import toctree as toctree_node
from sphinx.transforms import SphinxTransform
from sphinx.util.matching import Matcher

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n?", re.DOTALL)

# Keys that describe the filesystem structure itself. These are computed by
# sphinx-etoc from the filesystem layout and must never be overridden by
# frontmatter.
_STRUCTURAL_KEYS = {"root", "file", "entries", "subtrees"}

_DEFAULT_EXTENSIONS = [".md", ".rst"]


def _is_hidden(name: str) -> bool:
    return name.startswith(".")


def _natural_sort_key(name: str) -> List[Any]:
    """Numeric-aware sort key: "01" < "2" < "10" < "aaa", digits before letters."""
    return [
        (0, int(chunk)) if chunk.isdigit() else (1, chunk.lower())
        for chunk in re.split(r"(\d+)", name)
        if chunk
    ]


def _build_toc_item(
    dir_path: Path, source_dir: Path, extensions: List[str], index_name: str
) -> Optional[Dict[str, Any]]:
    """Recursively build a _toc.yml-shaped item for dir_path, or None if
    dir_path has no document files directly inside it -- there is no page to
    anchor a toctree node on. The caller (_collect_folder_entries) handles
    that case by making dir_path transparent rather than dropping it.

    A file named index_name (default "index") is always the folder's own
    entry; otherwise the folder's own entry is whichever document sorts
    first. All remaining files and subfolders are then interleaved and
    sorted together by name, so files no longer take precedence over
    subfolders regardless of name.
    """
    doc_files = [
        f
        for f in dir_path.iterdir()
        if f.is_file() and f.suffix in extensions and not _is_hidden(f.name)
    ]
    if not doc_files:
        return None

    doc_files.sort(key=lambda f: _natural_sort_key(f.stem))
    own_file = next((f for f in doc_files if f.stem == index_name), doc_files[0])

    children: List[Tuple[List[Any], Dict[str, Any]]] = [
        (_natural_sort_key(f.stem), {"file": _docname(f, source_dir)})
        for f in doc_files
        if f != own_file
    ]

    for sub_dir in dir_path.iterdir():
        if not sub_dir.is_dir() or _is_hidden(sub_dir.name):
            continue
        children.extend(_collect_folder_entries(sub_dir, source_dir, extensions, index_name))

    children.sort(key=lambda pair: pair[0])

    item: Dict[str, Any] = {"file": _docname(own_file, source_dir)}
    if children:
        item["entries"] = [child for _, child in children]
    return item


def _collect_folder_entries(
    dir_path: Path, source_dir: Path, extensions: List[str], index_name: str
) -> List[Tuple[List[Any], Dict[str, Any]]]:
    """The (sort_key, item) pairs dir_path contributes to its parent's
    entries list.

    Normally that's a single entry for dir_path's own toctree node, keyed by
    dir_path's name. A folder with no document file directly inside it has
    no page of its own to anchor a node on, so instead of dropping it (and
    everything nested below it), it is treated as transparent: each of its
    subfolders' own contributions bubbles up directly into the parent, as if
    dir_path itself didn't exist. A folder that is transparent all the way
    down (no document file anywhere below it) contributes nothing.
    """
    item = _build_toc_item(dir_path, source_dir, extensions, index_name)
    if item is not None:
        return [(_natural_sort_key(dir_path.name), item)]

    entries: List[Tuple[List[Any], Dict[str, Any]]] = []
    for sub_dir in dir_path.iterdir():
        if sub_dir.is_dir() and not _is_hidden(sub_dir.name):
            entries.extend(_collect_folder_entries(sub_dir, source_dir, extensions, index_name))
    return entries


def build_toc_from_filesystem(
    source_dir: Path,
    extensions: Optional[List[str]] = None,
    index_name: str = "index",
) -> Dict[str, Any]:
    """Build a _toc.yml-shaped dict by walking source_dir's own layout.

    Replaces `sphinx-etoc from-project`, which has two limitations this
    doesn't share:

    - It always lists a folder's own files before its subfolders, regardless
      of name. This walks the tree itself so that files and subfolders sort
      together by name (numeric-aware, e.g. "01" < "2" < "10" < "aaa"),
      matching how a reader scanning the filesystem would expect the table
      of contents to read.
    - It silently drops a folder with no document file directly inside it,
      along with everything nested below it, even if a deeper subfolder has
      real content. This instead treats such a folder as transparent: its
      subfolders' own toctree nodes bubble up into its parent directly, so
      nothing is lost. Only a folder with no document file anywhere below it
      (an empty branch) contributes nothing.
    """
    extensions = extensions or _DEFAULT_EXTENSIONS
    item = _build_toc_item(source_dir, source_dir, extensions, index_name)
    if item is None:
        raise ValueError(
            f"No {index_name}{tuple(extensions)} found under {source_dir}"
        )
    toc_data: Dict[str, Any] = {"root": item["file"]}
    if "entries" in item:
        toc_data["entries"] = item["entries"]
    return toc_data


def _docname(md_file: Path, source_dir: Path) -> str:
    return md_file.relative_to(source_dir).with_suffix("").as_posix()


def _read_frontmatter(md_file: Path) -> Dict[str, Any]:
    text = md_file.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else {}


def collect_toctree_options(
    source_dir: Path, exclude_patterns: Optional[List[str]] = None
) -> Dict[str, Dict[str, Any]]:
    """Collect the "toctree" frontmatter block of every *.md file below source_dir.

    Files matching exclude_patterns (Sphinx's own exclude_patterns, e.g. a
    downward-compatibility README.md) are skipped, since Sphinx won't build
    them either.

    Returns a mapping of docname (the file path relative to source_dir,
    without extension, as used by sphinx-etoc/sphinx-external-toc) to the
    options declared in that file's "toctree" frontmatter block.
    """
    matcher = Matcher(exclude_patterns or [])
    options_by_docname: Dict[str, Dict[str, Any]] = {}

    for md_file in sorted(source_dir.rglob("*.md")):
        if matcher(md_file.relative_to(source_dir).as_posix()):
            continue
        toctree = _read_frontmatter(md_file).get("toctree")
        if not isinstance(toctree, dict):
            continue
        toctree = {k: v for k, v in toctree.items() if k not in _STRUCTURAL_KEYS}
        if toctree:
            options_by_docname[_docname(md_file, source_dir)] = toctree

    return options_by_docname


def _apply(doc_item: Dict[str, Any], options_by_docname: Dict[str, Dict[str, Any]]) -> None:
    docname = doc_item.get("root", doc_item.get("file"))
    if docname is not None:
        toctree_options = options_by_docname.get(docname)
        if toctree_options:
            doc_item.update(toctree_options)

    for key in ("entries", "subtrees"):
        children = doc_item.get(key)
        if isinstance(children, list):
            for child in children:
                if isinstance(child, dict):
                    _apply(child, options_by_docname)


def apply_frontmatter_options(
    toc_data: Dict[str, Any], source_dir: Path, exclude_patterns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Merge every *.md file's "toctree" frontmatter options into toc_data.

    toc_data is a dict as returned by build_toc_from_filesystem().
    Modifies toc_data in place and returns it.
    """
    options_by_docname = collect_toctree_options(source_dir, exclude_patterns)
    if options_by_docname:
        _apply(toc_data, options_by_docname)
    return toc_data


def _relative_source_path(docname: str, source_dir: Path) -> Optional[str]:
    """Resolve a docname (as used in _toc.yml) to its file path, relative to
    source_dir, suffix included -- i.e. the form Sphinx's exclude_patterns
    are matched against.
    """
    for suffix in (".md", ".rst"):
        candidate = source_dir / f"{docname}{suffix}"
        if candidate.exists():
            return candidate.relative_to(source_dir).as_posix()
    return None


def _prune(doc_item: Dict[str, Any], source_dir: Path, matcher: Matcher) -> None:
    for key in ("entries", "subtrees"):
        children = doc_item.get(key)
        if not isinstance(children, list):
            continue

        kept = []
        for child in children:
            if isinstance(child, dict):
                docname = child.get("file")
                if docname is not None:
                    rel_path = _relative_source_path(docname, source_dir)
                    if rel_path is not None and matcher(rel_path):
                        continue
                _prune(child, source_dir, matcher)
            kept.append(child)

        if kept:
            doc_item[key] = kept
        else:
            del doc_item[key]


def prune_excluded_entries(
    toc_data: Dict[str, Any], source_dir: Path, exclude_patterns: List[str]
) -> Dict[str, Any]:
    """Drop entries that Sphinx's own exclude_patterns would exclude.

    build_toc_from_filesystem() derives _toc.yml purely from the filesystem
    and knows nothing about conf.py's exclude_patterns (e.g. a `README.md`
    kept for downward compatibility, or `_attachments`/`_listings`/`_unused`
    folders). Left unpruned, such an entry makes Sphinx fail with "toctree
    contains reference to nonexisting/excluded document" once warnings are
    treated as errors. An excluded entry is dropped along with its entire
    subtree, same as a folder without any files of its own.

    Modifies toc_data in place and returns it.
    """
    matcher = Matcher(exclude_patterns)
    _prune(toc_data, source_dir, matcher)
    return toc_data


class DropManualToctrees(SphinxTransform):
    """Silently drop explicit ``toctree`` directives in "filesystem" toctree mode.

    In "filesystem" toctree mode, the document hierarchy is derived from
    _toc.yml, generated from the source tree's own layout. An author may
    still leave (or copy-paste from "directive" mode) an explicit
    ```{toctree}``` directive in a document. Left in place,
    sphinx-external-toc's own InsertToctrees transform (priority 100) would
    warn "toctree directive not expected with external-toc" for it and,
    since hermesbaby builds with warnings-as-errors, fail the build -- even
    though the directive's content is redundant with _toc.yml and safe to
    ignore.

    Running at a lower priority than InsertToctrees removes such directives
    from the doctree beforehand, so they are tolerated and neglected instead
    of breaking the build.
    """

    default_priority = 90

    def apply(self, **kwargs: Any) -> None:
        for node in list(self.document.findall(toctree_node)):
            node.parent.remove(node)
