import pytest

from hermesbaby.drawio import DrawIOError
from hermesbaby.drawio.inline import (
    InlineDrawIOError,
    is_inline_source,
    parse_fence_arguments,
    store_inline_xml,
    validate_inline_xml,
)

VALID = '<mxfile><diagram id="a" name="p"><mxGraphModel/></diagram></mxfile>'


def test_fence_arguments_any_order():
    assert parse_fence_arguments("") == {"locked": False, "height": None}
    assert parse_fence_arguments("locked height=300") == {"locked": True, "height": 300}
    assert parse_fence_arguments("height=300 locked") == {"locked": True, "height": 300}


@pytest.mark.parametrize("arg", ["foo", "height=abc", "locked=1"])
def test_fence_arguments_unsupported(arg):
    with pytest.raises(InlineDrawIOError):
        parse_fence_arguments(arg)


def test_validate_ok():
    validate_inline_xml(VALID)


@pytest.mark.parametrize(
    "xml",
    [
        "",
        "   ",
        "<mxfile>",
        "<foo/>",
        "<mxfile></mxfile>",
        '<!DOCTYPE x [<!ENTITY a "b">]><mxfile><diagram/></mxfile>',
        "<mxfile><diagram>" + "a" * (5 * 1024 * 1024) + "</diagram></mxfile>",
    ],
)
def test_validate_rejects(xml):
    with pytest.raises(InlineDrawIOError):
        validate_inline_xml(xml)


def test_store_is_content_addressed(tmp_path):
    a = store_inline_xml(str(tmp_path), VALID)
    b = store_inline_xml(str(tmp_path), VALID)
    c = store_inline_xml(str(tmp_path), VALID.replace('"p"', '"q"'))
    assert a == b != c
    assert a.read_text().strip() == VALID
    assert is_inline_source(a, str(tmp_path))
    assert not is_inline_source(tmp_path / "x.drawio", str(tmp_path))


def _build(tmp_path, body):
    from sphinx.application import Sphinx

    src = tmp_path / "src"
    src.mkdir(exist_ok=True)
    (src / "conf.py").write_text(
        'extensions=["myst_parser","hermesbaby.drawio"]\n'
        'myst_fence_as_directive=["drawio"]\n'
        "drawio_headless=False\n"
    )
    (src / "index.md").write_text(body)
    app = Sphinx(str(src), str(src), str(tmp_path / "out"), str(tmp_path / "dt"), "dummy", status=None, warning=None)
    app.build()
    return app, src


def test_directive_creates_image_node_without_polluting_source(tmp_path):
    from docutils import nodes

    app, src = _build(tmp_path, f"# T\n\n```drawio locked height=300\n{VALID}\n```\n\n```xml\n<a/>\n```\n")
    doctree = app.env.get_doctree("index")
    images = list(doctree.findall(nodes.image))
    assert len(images) == 1 and "drawio" in images[0]["classes"]
    assert not list(src.rglob("*.drawio"))
    assert len(list((tmp_path / "dt" / "drawio-inline").glob("*.drawio"))) == 1


def test_directive_invalid_xml_fails(tmp_path):
    with pytest.raises(DrawIOError, match="index.md"):
        _build(tmp_path, "# T\n\n```drawio\n<mxfile>\n```\n")
