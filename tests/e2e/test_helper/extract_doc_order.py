"""Print the linear reading order of an HTML build, one docname per line.

Sphinx annotates every page's <head> with rel="next"/rel="prev" links that
reflect the order in which the page was visited while flattening the
toctree. Following rel="next" from the root page therefore reconstructs the
exact document tree order (both sorting and folder hierarchy) that the
"filesystem" toctree mode produced -- which is what these e2e tests need to
verify.

Usage:
    python extract_doc_order.py <path-to-html-build-dir>
"""

import re
import sys
from pathlib import Path

_LINK_RE = re.compile(r'<link rel="next"[^>]*href="([^"]*)"')


def _next_href(html_path: Path) -> str | None:
    match = _LINK_RE.search(html_path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def extract_order(html_root: Path) -> list[str]:
    html_root = html_root.resolve()
    order = []
    seen = set()
    current = html_root / "index.html"

    while True:
        docname = current.relative_to(html_root).with_suffix("").as_posix()
        if docname in seen:
            raise RuntimeError(f"cycle detected at {docname!r}")
        seen.add(docname)
        order.append(docname)

        href = _next_href(current)
        if not href:
            break
        current = (current.parent / href.split("#")[0]).resolve()

    return order


if __name__ == "__main__":
    for docname in extract_order(Path(sys.argv[1])):
        print(docname)
