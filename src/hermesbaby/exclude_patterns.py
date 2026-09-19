"""Compute Sphinx's `exclude_patterns` from a Kconfig-like config.

conf.py uses this to set Sphinx's own `exclude_patterns`. hermesbaby.filesystem_toc
uses the same list to keep a generated _toc.yml (filesystem toctree mode)
consistent with what Sphinx will actually build -- e.g. a `docs/README.md`
kept only for downward compatibility with reST projects must not end up
referenced by the generated toctree, since Sphinx itself won't build it.

A single shared function avoids the two lists drifting apart.
"""

from typing import List


def _exclude_any_depth(dir_name: str, ext: str = "") -> List[str]:
    return [
        f"{dir_name}/*{ext}",
        f"{dir_name}/**/*{ext}",
        f"**/{dir_name}/*{ext}",
        f"**/{dir_name}/**/*{ext}",
    ]


def compute_exclude_patterns(config) -> List[str]:
    """Compute Sphinx's exclude_patterns.

    :param config: anything exposing `config.syms[name].str_value`, i.e. a
        kconfiglib.Kconfig instance or a
        hermesbaby.kconfig_overrides.ConfigCompat.
    """
    return [
        config.syms["BUILD__DIRS__BUILD"].str_value + "/**",
        "README.md",
        *_exclude_any_depth(".git"),
        *_exclude_any_depth(".venv"),
        *_exclude_any_depth("_attachments"),
        *_exclude_any_depth("_listings"),
        *_exclude_any_depth("_unused"),
        *_exclude_any_depth(config.syms["I18N__DIR_LOCALES"].str_value),
    ]
