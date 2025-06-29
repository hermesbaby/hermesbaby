import re
import uuid

extensions.append("sphinx_markdown_checkbox")


def checkbox_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    inputs = re.split(r"[\[,\]]", text, 2)
    id = "cb_" + uuid.uuid4().hex
    if len(inputs) != 3:
        return
    checked = "checked" if inputs[1].lower() == "x" else ""
    node = nodes.raw(
        "",
        f'<input type="checkbox" id="{id}" {checked}/><label for="{id}">{inputs[2]}</label>',
        format="html",
    )
    return [node], []


roles.register_local_role("cb", checkbox_role)
