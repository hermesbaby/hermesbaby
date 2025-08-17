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
from sphinx.util.nodes import make_refnode

# --- Data model --------------------------------------------------------------


@dataclass
class Item:
    docname: str
    anchor: str
    title: str
    number: Tuple[int, ...] | None  # Sphinx "numfig" tuple if available


def _get_caption_or_title(table_or_figure: nodes.Node) -> str | None:
    for child in table_or_figure.children:
        if isinstance(child, nodes.caption):
            return child.astext().strip()
        if isinstance(child, nodes.title):
            return child.astext().strip()
    return None


# --- Custom placeholder nodes ------------------------------------------------


class list_of_figures_node(nodes.General, nodes.Element):
    pass


class list_of_tables_node(nodes.General, nodes.Element):
    pass


# --- Helpers for config & options -------------------------------------------


def _bool_opt(argument: str | None) -> bool:
    if argument is None:
        return True
    val = argument.strip().lower()
    return val in ("1", "true", "yes", "on")


def _get_conf(app: Sphinx, key: str, default: Any) -> Any:
    return getattr(app.config, key, default)


def _resolve_bool(value, default: bool) -> bool:
    if value is None:
        return default
    return bool(value)


def _format_number(number: Tuple[int, ...] | None) -> str:
    if not number:
        return ""
    return ".".join(str(n) for n in number)


# NEW in iteration_4.2: ensure figures/tables always have an anchor
def _ensure_anchor(env: BuildEnvironment, node: nodes.Node, kind: str) -> str | None:
    if node.get("ids"):
        return node["ids"][0]

    parent = node.parent
    if parent is None:
        return None

    serial = env.new_serialno(f"loflot-{kind}")
    anchor = f"loflot-{kind}-{serial}"
    tgt = nodes.target("", "", ids=[anchor])
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
        node = list_of_figures_node("")
        node["caption"] = self.options.get("caption")
        node["include_uncaptioned"] = self.options.get("include-uncaptioned")
        node["uncaptioned_label"] = self.options.get("uncaptioned-label")
        node["empty_message"] = self.options.get("empty-message")
        return [node]


class ListOfTables(Directive):
    has_content = False
    option_spec = {
        "caption": directives.unchanged,
        "include-uncaptioned": _bool_opt,
        "uncaptioned-label": directives.unchanged,
        "empty-message": directives.unchanged,
    }

    def run(self):
        node = list_of_tables_node("")
        node["caption"] = self.options.get("caption")
        node["include_uncaptioned"] = self.options.get("include-uncaptioned")
        node["uncaptioned_label"] = self.options.get("uncaptioned-label")
        node["empty_message"] = self.options.get("empty-message")
        return [node]


# --- Sphinx integration ------------------------------------------------------


def _ensure_store(env: BuildEnvironment) -> Dict[str, List[Item]]:
    if "sphinx_loflot" not in env.domaindata:
        env.domaindata["sphinx_loflot"] = {"figs": [], "tabs": []}
    return env.domaindata["sphinx_loflot"]  # type: ignore[return-value]


def _clear_doc(env: BuildEnvironment, docname: str) -> None:
    store = _ensure_store(env)
    store["figs"] = [i for i in store["figs"] if i.docname != docname]
    store["tabs"] = [i for i in store["tabs"] if i.docname != docname]


def _collect_num(env: BuildEnvironment, node: nodes.Node) -> Tuple[int, ...] | None:
    try:
        fig_nums = getattr(env, "toc_fignumbers", {}) or {}
    except Exception:
        fig_nums = {}
    try:
        tab_nums = getattr(env, "toc_tablenumbers", {}) or {}
    except Exception:
        tab_nums = {}

    for _id in node.get("ids", []):
        for mapping in (fig_nums, tab_nums):
            for _doc, bytype in mapping.items():
                for _kind, ids_map in bytype.items():
                    if _id in ids_map:
                        return ids_map[_id]
    return None


def on_doctree_read(app: Sphinx, doctree: nodes.document) -> None:
    env = app.env
    assert env is not None
    docname = env.docname
    store = _ensure_store(env)
    _clear_doc(env, docname)

    for fig in doctree.traverse(nodes.figure):
        anchor = _ensure_anchor(env, fig, "figure")
        if not anchor:
            continue
        title = _get_caption_or_title(fig)
        store["figs"].append(
            Item(
                docname, anchor, title.strip() if title else "", _collect_num(env, fig)
            )
        )

    for tab in doctree.traverse(nodes.table):
        anchor = _ensure_anchor(env, tab, "table")
        if not anchor:
            continue
        title = _get_caption_or_title(tab)
        store["tabs"].append(
            Item(
                docname, anchor, title.strip() if title else "", _collect_num(env, tab)
            )
        )


def on_env_purge_doc(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    _clear_doc(env, docname)


def on_env_merge_info(
    app: Sphinx, env: BuildEnvironment, docnames: List[str], other: BuildEnvironment
) -> None:
    store = _ensure_store(env)
    other_store = _ensure_store(other)
    store["figs"].extend([i for i in other_store["figs"] if i.docname in docnames])
    store["tabs"].extend([i for i in other_store["tabs"] if i.docname in docnames])


# --- Building lists ----------------------------------------------------------


def _new_section_with_id(env: BuildEnvironment, kind: str) -> nodes.section:
    serial = env.new_serialno("loflot-section")
    sec_id = f"loflot-{kind}-section-{serial}"
    return nodes.section(ids=[sec_id])


def _build_list(
    app: Sphinx,
    kind: str,
    fromdocname: str,
    items: List[Item],
    caption: str | None,
    include_uncaptioned: bool,
    uncaptioned_label: str,
    empty_message: str,
) -> nodes.Node:
    items_sorted = sorted(items, key=lambda i: (i.docname, i.anchor))
    env = app.env
    assert env is not None

    container = _new_section_with_id(env, kind)
    if caption:
        container += nodes.title(text=caption)

    blist = nodes.bullet_list()
    added = False
    for it in items_sorted:
        has_title = bool(it.title)
        if not has_title and not include_uncaptioned:
            continue
        display_title = it.title if has_title else uncaptioned_label

        para = nodes.paragraph()
        numtxt = _format_number(it.number)
        if numtxt:
            para += nodes.inline(text=f"{numtxt} — ")

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
    app: Sphinx,
    placeholder_node: nodes.Element,
    kind: str,
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


def on_doctree_resolved(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    env = app.env
    assert env is not None
    store = _ensure_store(env)

    default_include_uncaptioned_figs = _get_conf(
        app, "loflot_include_uncaptioned_figures", True
    )
    default_include_uncaptioned_tabs = _get_conf(
        app, "loflot_include_uncaptioned_tables", True
    )
    default_label_fig = _get_conf(
        app, "loflot_uncaptioned_label_figure", _("[No caption]")
    )
    default_label_tab = _get_conf(
        app, "loflot_uncaptioned_label_table", _("[No title]")
    )
    default_empty_fig = _get_conf(
        app, "loflot_empty_message_figures", _("(no figures)")
    )
    default_empty_tab = _get_conf(app, "loflot_empty_message_tables", _("(no tables)"))

    for node in list(doctree.traverse(list_of_figures_node)):
        if _maybe_replace_with_latex_native(app, node, "figures"):
            continue
        caption = node.get("caption") or None
        include_uncaptioned = _resolve_bool(
            node.get("include_uncaptioned"), default_include_uncaptioned_figs
        )
        uncaptioned_label = node.get("uncaptioned_label") or default_label_fig
        empty_message = node.get("empty_message") or default_empty_fig
        new = _build_list(
            app,
            "figures",
            docname,
            store["figs"],
            caption,
            include_uncaptioned,
            uncaptioned_label,
            empty_message,
        )
        node.replace_self(new)

    for node in list(doctree.traverse(list_of_tables_node)):
        if _maybe_replace_with_latex_native(app, node, "tables"):
            continue
        caption = node.get("caption") or None
        include_uncaptioned = _resolve_bool(
            node.get("include_uncaptioned"), default_include_uncaptioned_tabs
        )
        uncaptioned_label = node.get("uncaptioned_label") or default_label_tab
        empty_message = node.get("empty_message") or default_empty_tab
        new = _build_list(
            app,
            "tables",
            docname,
            store["tabs"],
            caption,
            include_uncaptioned,
            uncaptioned_label,
            empty_message,
        )
        node.replace_self(new)


# --- Setup ------------------------------------------------------------------


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_node(list_of_figures_node)
    app.add_node(list_of_tables_node)
    app.add_directive("list-of-figures", ListOfFigures)
    app.add_directive("list-of-tables", ListOfTables)

    app.connect("doctree-read", on_doctree_read)
    app.connect("env-purge-doc", on_env_purge_doc)
    app.connect("env-merge-info", on_env_merge_info)
    app.connect("doctree-resolved", on_doctree_resolved)

    app.add_config_value("loflot_include_uncaptioned_figures", True, "env")
    app.add_config_value("loflot_include_uncaptioned_tables", True, "env")
    app.add_config_value("loflot_uncaptioned_label_figure", _("[No caption]"), "env")
    app.add_config_value("loflot_uncaptioned_label_table", _("[No title]"), "env")
    app.add_config_value("loflot_latex_behavior", "passthrough", "env")
    app.add_config_value("loflot_empty_message_figures", _("(no figures)"), "env")
    app.add_config_value("loflot_empty_message_tables", _("(no tables)"), "env")

    return {
        "version": "0.4.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
