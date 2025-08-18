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

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.locale import _
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util.nodes import make_refnode

# --- Data model --------------------------------------------------------------


@dataclass
class Item:
    docname: str
    anchor: str  # primary link target (always exists)
    ids_for_numbering: List[str]  # ids that might carry the numfig number
    title: str


# --- Utilities ---------------------------------------------------------------


def _get_caption_or_title(node: nodes.Node) -> str | None:
    for ch in node.children:
        if isinstance(ch, nodes.caption):
            return ch.astext().strip()
        if isinstance(ch, nodes.title):
            return ch.astext().strip()
    return None


def _descendant_ids(node: nodes.Node, kinds=(nodes.caption, nodes.title)) -> List[str]:
    out: List[str] = []
    for k in kinds:
        for ch in node.traverse(k):
            out.extend(ch.get("ids", []))
    return out


class list_of_figures_node(nodes.General, nodes.Element):
    pass


class list_of_tables_node(nodes.General, nodes.Element):
    pass


def _bool_opt(arg: str | None) -> bool:
    if arg is None:
        return True
    return arg.strip().lower() in ("1", "true", "yes", "on")


def _get_conf(app: Sphinx, key: str, default: Any) -> Any:
    return getattr(app.config, key, default)


def _resolve_bool(value, default: bool) -> bool:
    return default if value is None else bool(value)


def _format_number(num: Tuple[int, ...] | None) -> str:
    return "" if not num else ".".join(str(n) for n in num)


def _ensure_anchor(env: BuildEnvironment, node: nodes.Node, kind: str) -> str:
    if node.get("ids"):
        return node["ids"][0]
    parent = node.parent
    serial = env.new_serialno(f"loflot-{kind}")
    anchor = f"loflot-{kind}-{serial}"
    tgt = nodes.target("", "", ids=[anchor])
    if parent is not None:
        parent.insert(parent.index(node), tgt)
    return anchor


# --- Directives --------------------------------------------------------------


class ListOfFigures(Directive):
    has_content = False
    option_spec = {
        "caption": directives.unchanged,
        "include-uncaptioned": _bool_opt,
        "uncaptioned-label": directives.unchanged,
        "empty-message": directives.unchanged,
    }

    def run(self):
        n = list_of_figures_node("")
        n["caption"] = self.options.get("caption")
        n["include_uncaptioned"] = self.options.get("include-uncaptioned")
        n["uncaptioned_label"] = self.options.get("uncaptioned-label")
        n["empty_message"] = self.options.get("empty-message")
        return [n]


class ListOfTables(Directive):
    has_content = False
    option_spec = {
        "caption": directives.unchanged,
        "include-uncaptioned": _bool_opt,
        "uncaptioned-label": directives.unchanged,
        "empty-message": directives.unchanged,
    }

    def run(self):
        n = list_of_tables_node("")
        n["caption"] = self.options.get("caption")
        n["include_uncaptioned"] = self.options.get("include-uncaptioned")
        n["uncaptioned_label"] = self.options.get("uncaptioned-label")
        n["empty_message"] = self.options.get("empty-message")
        return [n]


# --- Sphinx integration: collect --------------------------------------------


def _ensure_store(env: BuildEnvironment) -> Dict[str, List[Item]]:
    if "sphinx_loflot" not in env.domaindata:
        env.domaindata["sphinx_loflot"] = {"figs": [], "tabs": []}
    return env.domaindata["sphinx_loflot"]  # type: ignore[return-value]


def _clear_doc(env: BuildEnvironment, docname: str) -> None:
    store = _ensure_store(env)
    store["figs"] = [i for i in store["figs"] if i.docname != docname]
    store["tabs"] = [i for i in store["tabs"] if i.docname != docname]


def on_doctree_read(app: Sphinx, doctree: nodes.document) -> None:
    env = app.env
    assert env is not None
    docname = env.docname
    store = _ensure_store(env)
    _clear_doc(env, docname)

    # Figures
    for fig in doctree.traverse(nodes.figure):
        anchor = _ensure_anchor(env, fig, "figure")
        title = (_get_caption_or_title(fig) or "").strip()
        candidates: List[str] = []
        if fig.get("ids"):
            candidates.extend(fig["ids"])
        candidates.extend(_descendant_ids(fig))
        if anchor not in candidates:
            candidates.insert(0, anchor)
        store["figs"].append(Item(docname, anchor, candidates, title))

    # Tables
    for tab in doctree.traverse(nodes.table):
        anchor = _ensure_anchor(env, tab, "table")
        title = (_get_caption_or_title(tab) or "").strip()
        candidates: List[str] = []
        if tab.get("ids"):
            candidates.extend(tab["ids"])
        candidates.extend(_descendant_ids(tab))
        if anchor not in candidates:
            candidates.insert(0, anchor)
        store["tabs"].append(Item(docname, anchor, candidates, title))


def on_env_purge_doc(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    _clear_doc(env, docname)


def on_env_merge_info(
    app: Sphinx, env: BuildEnvironment, docnames: List[str], other: BuildEnvironment
) -> None:
    store = _ensure_store(env)
    other_store = _ensure_store(other)
    store["figs"].extend([i for i in other_store["figs"] if i.docname in docnames])
    store["tabs"].extend([i for i in other_store["tabs"] if i.docname in docnames])


# --- Fallback numbering (theme-agnostic) ------------------------------------


def _build_fallback_numbers(
    env: BuildEnvironment,
) -> Dict[str, Dict[str, Dict[tuple, int]]]:
    """
    Returns: {kind: {'order': {(docname, anchor): ordinal}}}
    where kind is 'figures' or 'tables'. Order is stable by (docname, anchor).
    """
    store = _ensure_store(env)
    out: Dict[str, Dict[str, Dict[tuple, int]]] = {
        "figures": {"order": {}},
        "tables": {"order": {}},
    }
    for kind in ("figures", "tables"):
        items = sorted(
            store["figs" if kind == "figures" else "tabs"],
            key=lambda i: (i.docname, i.anchor),
        )
        n = 0
        order: Dict[tuple, int] = {}
        for it in items:
            n += 1
            order[(it.docname, it.anchor)] = n
        out[kind]["order"] = order
    return out


_FALLBACK_CACHE: Dict[int, Dict[str, Dict[str, Dict[tuple, int]]]] = {}


def _fallback_number(
    env: BuildEnvironment, kind: str, docname: str, anchor: str
) -> Tuple[int, ...] | None:
    # Cache per build (env object identity)
    key = id(env)
    cache = _FALLBACK_CACHE.get(key)
    if cache is None:
        cache = _build_fallback_numbers(env)
        _FALLBACK_CACHE[key] = cache
    ordmap = cache[kind]["order"]
    num = ordmap.get((docname, anchor))
    return (num,) if num else None


# --- Number lookup -----------------------------------------------------------


def _lookup_number(
    env: BuildEnvironment,
    kind: str,
    docname: str,
    id_candidates: List[str],
    anchor_for_fallback: str | None = None,
) -> Tuple[int, ...] | None:
    """Prefer std domain’s numbers; then env maps; finally theme-agnostic fallback."""
    typ = "figure" if kind == "figures" else "table"

    # 1) std domain API
    try:
        std = env.get_domain("std")  # type: ignore[attr-defined]
    except Exception:
        std = None
    if std is not None and hasattr(std, "get_fignumber"):
        for cid in id_candidates:
            try:
                n = std.get_fignumber(env, docname, typ, cid)  # type: ignore[misc]
                if n:
                    return n
            except Exception:
                pass

    # 2) env fallback maps
    try:
        mapping = (
            getattr(
                env, "toc_fignumbers" if typ == "figure" else "toc_tablenumbers", {}
            )
            or {}
        )
        bytype = mapping.get(docname, {})
        ids_map = bytype.get(typ, {})
        for cid in id_candidates:
            if cid in ids_map:
                return ids_map[cid]
    except Exception:
        pass

    # 3) deterministic fallback if theme hides official numbers
    if anchor_for_fallback:
        return _fallback_number(env, kind, docname, anchor_for_fallback)
    return None


def _numlabel_prefix(app: Sphinx, kind: str, number: Tuple[int, ...] | None) -> str:
    if not number:
        return ""
    cfg = getattr(app.config, "numfig_format", None)
    label = _("Figure") if kind == "figures" else _("Table")
    numtxt = _format_number(number)
    if isinstance(cfg, dict) and ("figure" in cfg or "table" in cfg):
        fmt = cfg.get("figure" if kind == "figures" else "table", f"{label} %s")
        try:
            return fmt.replace("%s", numtxt) + ": "
        except Exception:
            return f"{label} {numtxt}: "
    return f"{label} {numtxt}: "


# --- Post-transform (runs during writing, when numbers are finalized) --------


class LoflotPostTransform(SphinxPostTransform):
    default_priority = 999  # run late

    def run(self) -> None:
        app = self.app
        env = self.env
        docname = env.docname  # the doc currently being written

        # Replace figure lists
        for node in list(self.document.traverse(list_of_figures_node)):
            if _maybe_replace_with_latex_native(app, node, "figures"):
                continue
            caption = node.get("caption") or None
            include_uncaptioned = _resolve_bool(
                node.get("include_uncaptioned"),
                _get_conf(app, "loflot_include_uncaptioned_figures", True),
            )
            uncaptioned_label = node.get("uncaptioned_label") or _("[No caption]")
            empty_message = node.get("empty_message") or _get_conf(
                app, "loflot_empty_message_figures", _("(no figures)")
            )
            new = _build_list_node(
                app,
                "figures",
                docname,
                _ensure_store(env)["figs"],
                caption,
                include_uncaptioned,
                uncaptioned_label,
                empty_message,
            )
            node.replace_self(new)

        # Replace table lists
        for node in list(self.document.traverse(list_of_tables_node)):
            if _maybe_replace_with_latex_native(app, node, "tables"):
                continue
            caption = node.get("caption") or None
            include_uncaptioned = _resolve_bool(
                node.get("include_uncaptioned"),
                _get_conf(app, "loflot_include_uncaptioned_tables", True),
            )
            uncaptioned_label = node.get("uncaptioned_label") or _("[No title]")
            empty_message = node.get("empty_message") or _get_conf(
                app, "loflot_empty_message_tables", _("(no tables)")
            )
            new = _build_list_node(
                app,
                "tables",
                docname,
                _ensure_store(env)["tabs"],
                caption,
                include_uncaptioned,
                uncaptioned_label,
                empty_message,
            )
            node.replace_self(new)


def _new_section_with_id(env: BuildEnvironment, kind: str) -> nodes.section:
    sec_id = f"loflot-{kind}-section-{env.new_serialno('loflot-section')}"
    return nodes.section(ids=[sec_id])


def _build_list_node(
    app: Sphinx,
    kind: str,  # "figures" | "tables"
    fromdocname: str,
    items: List[Item],
    caption: str | None,
    include_uncaptioned: bool,
    uncaptioned_label: str,
    empty_message: str,
) -> nodes.Node:
    env = app.env
    assert env is not None
    items_sorted = sorted(items, key=lambda i: (i.docname, i.anchor))

    container = _new_section_with_id(env, kind)
    if caption:
        container += nodes.title(text=caption)

    blist = nodes.bullet_list()
    added = False

    for it in items_sorted:
        has_title = bool(it.title)
        if not has_title and not include_uncaptioned:
            continue

        number = _lookup_number(
            env, kind, it.docname, it.ids_for_numbering, anchor_for_fallback=it.anchor
        )
        prefix = _numlabel_prefix(app, kind, number)
        display_title = it.title if has_title else uncaptioned_label

        para = nodes.paragraph()
        if prefix:
            para += nodes.inline(text=prefix)

        ref = make_refnode(
            app.builder,
            fromdocname,
            it.docname,
            it.anchor,
            nodes.literal(text=display_title),
            it.anchor,
        )
        para += ref

        blist += nodes.list_item("", para)
        added = True

    if not added:
        blist += nodes.list_item("", nodes.paragraph(text=empty_message))

    container += blist
    return container


def _maybe_replace_with_latex_native(
    app: Sphinx, placeholder_node: nodes.Element, kind: str
) -> bool:
    builder = getattr(app, "builder", None)
    behavior = _get_conf(app, "loflot_latex_behavior", "passthrough")
    if not builder or builder.name != "latex":
        return False
    if str(behavior).lower() != "passthrough":
        return False
    raw = nodes.raw(
        text=(r"\listoffigures" if kind == "figures" else r"\listoftables"),
        format="latex",
    )
    placeholder_node.replace_self(raw)
    return True


# --- Setup ------------------------------------------------------------------


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_node(list_of_figures_node)
    app.add_node(list_of_tables_node)
    app.add_directive("list-of-figures", ListOfFigures)
    app.add_directive("list-of-tables", ListOfTables)

    app.connect("doctree-read", on_doctree_read)
    app.connect("env-purge-doc", on_env_purge_doc)
    app.connect("env-merge-info", on_env_merge_info)

    # Replace placeholders at write time (numbers finalized or fallback)
    app.add_post_transform(LoflotPostTransform)

    app.add_config_value("loflot_include_uncaptioned_figures", True, "env")
    app.add_config_value("loflot_include_uncaptioned_tables", True, "env")
    app.add_config_value("loflot_uncaptioned_label_figure", _("[No caption]"), "env")
    app.add_config_value("loflot_uncaptioned_label_table", _("[No title]"), "env")
    app.add_config_value("loflot_latex_behavior", "passthrough", "env")
    app.add_config_value("loflot_empty_message_figures", _("(no figures)"), "env")
    app.add_config_value("loflot_empty_message_tables", _("(no tables)"), "env")

    return {"version": "0.5.1", "parallel_read_safe": True, "parallel_write_safe": True}
