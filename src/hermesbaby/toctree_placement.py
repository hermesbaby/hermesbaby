"""Normalize where a document's toctree ends up in the rendered page.

A document's toctree can end up almost anywhere in the doctree, depending on
how it got there:

- "directive" toctree mode: an author writes an explicit ```{toctree}```
  directive, and it renders wherever in the document they happened to put
  it -- top level, or nested inside some subsection.
- "filesystem" toctree mode: sphinx-external-toc's ``InsertToctrees``
  transform generates the toctree and appends it to the last section it
  finds, which in practice usually means "after all of the document's own
  content", regardless of that content's structure.

Either way, the position is incidental rather than intentional, which reads
oddly to a reader: entries can show up before/after arbitrary subsections
with no clear rule. This module normalizes it: every toctree found in a
document is moved to right before that document's first nested chapter
(the first heading-level child section right under the document's title),
or appended at the very end if the document has no nested chapter.
"""

from typing import Any, List

from docutils import nodes
from sphinx.addnodes import toctree as toctree_node
from sphinx.transforms import SphinxTransform


def _movable_node(node: nodes.Node) -> nodes.Node:
    """Return the node to relocate: the ``toctree-wrapper`` compound around
    ``node`` if there is one (as both directive and filesystem mode produce),
    else ``node`` itself.
    """
    parent = node.parent
    if isinstance(parent, nodes.compound) and "toctree-wrapper" in parent.get(
        "classes", []
    ):
        return parent
    return node


class NormalizeToctreePlacement(SphinxTransform):
    """Move every toctree in a document to right before its first chapter."""

    # After sphinx-external-toc's InsertToctrees (priority 100), and after
    # docutils/Sphinx have parsed any explicit ``{toctree}`` directives
    # (already present in the doctree by the time any transform runs).
    default_priority = 200

    def apply(self, **kwargs: Any) -> None:
        doctree = self.document

        seen = set()
        nodes_to_move: List[nodes.Node] = []
        for node in doctree.findall(toctree_node):
            movable = _movable_node(node)
            if id(movable) in seen:
                continue
            seen.add(id(movable))
            nodes_to_move.append(movable)

        if not nodes_to_move:
            return

        root_section = next(
            (child for child in doctree.children if isinstance(child, nodes.section)),
            None,
        )
        container = root_section if root_section is not None else doctree

        for node in nodes_to_move:
            node.parent.remove(node)

        insert_index = len(container.children)
        for index, child in enumerate(container.children):
            if isinstance(child, nodes.section):
                insert_index = index
                break

        for offset, node in enumerate(nodes_to_move):
            container.insert(insert_index + offset, node)
