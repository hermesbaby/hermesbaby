"""Inline draw.io diagrams in MyST Markdown fenced blocks.

A fence like

    ```drawio locked height=300
    <mxfile>...</mxfile>
    ```

is turned (via ``myst_fence_as_directive``) into the ``drawio`` directive
implemented here. The XML is validated and stored content-addressed in the
Sphinx doctree directory (never in the source tree). The directive then emits an
image node marked with the ``drawio`` class, so that the existing
``DrawIOConverter`` renders it like any external ``.drawio`` file.
"""

import os
import re
import tempfile
from hashlib import sha1
from pathlib import Path
from typing import List
from xml.etree import ElementTree as ET

from docutils import nodes
from docutils.nodes import Node

from sphinx.util.docutils import SphinxDirective

INLINE_DIR_NAME = "drawio-inline"

# Upper limit for the embedded XML (characters)
MAX_INLINE_XML_SIZE = 5 * 1024 * 1024

# Editor-only metadata of the VS Code Draw.io Integration. Does not affect published output.
_HEIGHT_RE = re.compile(r"^height=\d+$")
_UNSAFE_XML_RE = re.compile(r"<!\s*(DOCTYPE|ENTITY)", re.IGNORECASE)


class InlineDrawIOError(ValueError):
    """Raised when an embedded draw.io diagram is invalid."""


def parse_fence_arguments(arguments: str) -> dict:
    """Parse the fence header (text after ``drawio``), e.g. ``locked height=300``."""
    result = {"locked": False, "height": None}
    for token in (arguments or "").split():
        if token == "locked":
            result["locked"] = True
        elif _HEIGHT_RE.match(token):
            result["height"] = int(token.split("=", 1)[1])
        else:
            raise InlineDrawIOError(
                f"unsupported drawio fence attribute '{token}' (supported: 'locked', 'height=N')"
            )
    return result


def validate_inline_xml(xml: str) -> None:
    """Validate embedded draw.io XML. Raises InlineDrawIOError on problems."""
    if not xml.strip():
        raise InlineDrawIOError("embedded draw.io diagram is empty")
    if len(xml) > MAX_INLINE_XML_SIZE:
        raise InlineDrawIOError(
            f"embedded draw.io diagram exceeds the size limit of {MAX_INLINE_XML_SIZE} characters"
        )
    if _UNSAFE_XML_RE.search(xml):
        raise InlineDrawIOError(
            "DOCTYPE and ENTITY declarations are not allowed in embedded draw.io diagrams"
        )
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise InlineDrawIOError(f"embedded draw.io diagram is not well-formed XML: {exc}")
    if root.tag != "mxfile":
        raise InlineDrawIOError(
            f"embedded draw.io diagram must have <mxfile> as root element, got <{root.tag}>"
        )
    if not any(child.tag == "diagram" for child in root):
        raise InlineDrawIOError("embedded draw.io <mxfile> contains no <diagram>")


def inline_cache_dir(doctreedir: str) -> Path:
    return Path(doctreedir) / INLINE_DIR_NAME


def is_inline_source(path: Path, doctreedir: str) -> bool:
    """True if ``path`` is a generated representation of an inline diagram."""
    try:
        Path(os.path.abspath(path)).relative_to(os.path.abspath(inline_cache_dir(doctreedir)))
        return True
    except ValueError:
        return False


def store_inline_xml(doctreedir: str, xml: str) -> Path:
    """Write the XML content-addressed (atomically) and return the file path."""
    data = xml.strip() + "\n"
    digest = sha1(data.encode("utf-8")).hexdigest()
    target_dir = inline_cache_dir(doctreedir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{digest}.drawio"
    if not target.exists():
        fd, tmp = tempfile.mkstemp(dir=target_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(data)
            os.replace(tmp, target)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
    return target


class InlineDrawIO(SphinxDirective):
    """Directive ``drawio`` rendering the XML given as content."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self) -> List[Node]:
        source, line = self.get_source_info()
        try:
            parse_fence_arguments(self.arguments[0] if self.arguments else "")
            xml = "\n".join(self.content)
            validate_inline_xml(xml)
        except InlineDrawIOError as exc:
            from . import DrawIOError

            raise DrawIOError(f"{source}:{line}: {exc}")

        path = store_inline_xml(self.env.app.doctreedir, xml)
        rel = os.path.relpath(path, self.env.srcdir).replace(os.sep, "/")
        image = nodes.image(uri="/" + rel, alt="draw.io diagram", classes=["drawio"])
        self.set_source_info(image)
        return [image]
