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

import json
import os
import shutil
import sys
import tarfile
from pathlib import Path

import pytest

# The CLI imports the module as hermesbaby.tinytex, so patch that one
from hermesbaby import tinytex


@pytest.mark.parametrize(
    "version, system, machine, expected",
    [
        (None, "Linux", "x86_64", "daily/TinyTeX-1.tar.gz"),
        (None, "Darwin", "arm64", "daily/TinyTeX-1.tgz"),
        (None, "Windows", "AMD64", "daily/TinyTeX-1.zip"),
        ("2026.10", "Linux", "x86_64", "v2026.10/TinyTeX-1-v2026.10.tar.gz"),
        ("v2026.10", "Windows", "AMD64", "v2026.10/TinyTeX-1-v2026.10.zip"),
    ],
)
def test_download_url(monkeypatch, version, system, machine, expected):
    monkeypatch.delenv(tinytex.ENV_TINYTEX_VERSION, raising=False)
    assert tinytex.download_url(version, system, machine) == f"{tinytex.TINYTEX_RELEASES_URL}/{expected}"


def test_download_url_unsupported_platform():
    with pytest.raises(tinytex.TinyTexError):
        tinytex.download_url(None, "Linux", "aarch64")


def test_root_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv(tinytex.ENV_TINYTEX_DIR, str(tmp_path / "tt"))
    assert tinytex.root_dir() == tmp_path / "tt"


def test_required_packages_cover_preamble():
    packages = tinytex.required_packages()
    assert len(packages) == len(set(packages))
    for p in ("luatex", "latexmk", "dejavu", "fontspec", "babel", "adjustbox", "setspace"):
        assert p in packages
    assert all(" " not in p and "#" not in p for p in packages)


def test_missing_files_from_log():
    log = """
! LaTeX Error: File `titlesec.sty' not found.
! I can't find file `foo.cls'.
! LaTeX Error: File `titlesec.sty' not found.
module 'luaotfload-main' not found:
"""
    assert tinytex.missing_files_from_log(log) == ["titlesec.sty", "foo.cls", "luaotfload-main.lua"]


def test_parse_tlmgr_file_search():
    output = """tlmgr: package repository https://mirror.ctan.org/systems/texlive/tlnet (verified)
titlesec:
\ttexmf-dist/tex/latex/titlesec/titlesec.sty
other:
\ttexmf-dist/tex/latex/other/nottitlesec.sty
"""
    assert tinytex.parse_tlmgr_file_search(output, "titlesec.sty") == ["titlesec"]


def _fake_bundle(tmp_path: Path) -> Path:
    """A TinyTeX-like tarball whose tools only log their arguments."""
    top = tmp_path / "bundle" / ".TinyTeX"
    bin_dir = top / "bin" / "x86_64-linux"
    bin_dir.mkdir(parents=True)
    script = '#!/bin/sh\necho "$(basename "$0") $* TEXMFVAR=$TEXMFVAR" >> "$(dirname "$0")/../../calls.log"\n'
    for name in ("tlmgr", "luaotfload-tool"):
        f = bin_dir / name
        f.write_text(script)
        f.chmod(0o755)
    archive = tmp_path / "TinyTeX-1.tar.gz"
    with tarfile.open(archive, "w:gz") as t:
        t.add(top, arcname=".TinyTeX")
    return archive


@pytest.mark.skipif(sys.platform == "win32", reason="fake tools are shell scripts")
def test_install_check_uninstall(monkeypatch, tmp_path, cli_runner):
    from src.hermesbaby.__main__ import app

    root = tmp_path / "home" / "TinyTeX"
    monkeypatch.setenv(tinytex.ENV_TINYTEX_DIR, str(root))
    archive = _fake_bundle(tmp_path)
    monkeypatch.setattr(tinytex, "download_url", lambda version=None: "https://example.invalid/TinyTeX-1.tar.gz")
    monkeypatch.setattr(tinytex, "_download", lambda url, target, echo: shutil.copy(archive, target))

    result = cli_runner.invoke(app, ["tools", "latex", "check"])
    assert result.exit_code == 1

    result = cli_runner.invoke(app, ["tools", "latex", "install"])
    assert result.exit_code == 0, result.output

    calls = (root / "calls.log").read_text().splitlines()
    assert calls[0].startswith("tlmgr update --self")
    assert calls[1].startswith("tlmgr install " + " ".join(tinytex.required_packages()))
    assert calls[2].startswith("luaotfload-tool --update")
    # Font cache and user trees stay inside the installation
    assert all(c.endswith(f"TEXMFVAR={root / 'texmf-var'}") for c in calls)

    marker = json.loads((root / tinytex.MARKER_FILE).read_text())
    assert set(marker["packages"]) == set(tinytex.required_packages())

    result = cli_runner.invoke(app, ["tools", "latex", "check"])
    assert result.exit_code == 0, result.output
    assert "complete" in result.output

    result = cli_runner.invoke(app, ["tools", "latex", "path"])
    assert result.output.strip() == str(root / "bin" / "x86_64-linux")

    # Re-running install keeps the existing bundle
    monkeypatch.setattr(tinytex, "_download", lambda *a: pytest.fail("downloaded again"))
    result = cli_runner.invoke(app, ["tools", "latex", "install"])
    assert result.exit_code == 0, result.output

    result = cli_runner.invoke(app, ["tools", "latex", "uninstall", "--yes"])
    assert result.exit_code == 0
    assert not root.exists()


def test_build_env_prepends_tinytex(monkeypatch, tmp_path):
    root = tmp_path / "TinyTeX"
    (root / "bin" / "windows").mkdir(parents=True)
    (root / "bin" / "windows" / "tlmgr.bat").write_text("")
    env = tinytex.build_env({"PATH": "/usr/bin"}, root=root)
    assert env["PATH"] == str(root / "bin" / "windows") + os.pathsep + "/usr/bin"
    assert env["TEXMFHOME"] == str(root / "texmf-home")


def test_latex_prepare_env(monkeypatch, tmp_path):
    from src.hermesbaby import __main__ as hb

    monkeypatch.setenv(tinytex.ENV_TINYTEX_DIR, str(tmp_path / "none"))

    # Neither TinyTeX nor a TeX distribution on PATH
    assert hb._latex_prepare_env({"PATH": str(tmp_path)}) is False

    # System TeX on PATH (CI)
    for name in ("latexmk", "lualatex"):
        f = tmp_path / name
        f.write_text("")
        f.chmod(0o755)
    if sys.platform != "win32":
        assert hb._latex_prepare_env({"PATH": str(tmp_path)}) is True


@pytest.mark.skipif(
    sys.platform == "win32" or not (shutil.which("latexmk") and shutil.which("lualatex")),
    reason="needs a TeX distribution on PATH",
)
def test_doctor_with_real_latex(monkeypatch, tmp_path, cli_runner):
    """doctor detects a missing package from a real LuaLaTeX log and installs its provider."""
    from src.hermesbaby.__main__ import app

    root = tmp_path / "TinyTeX"
    bin_dir = root / "bin" / "x86_64-linux"
    bin_dir.mkdir(parents=True)
    for name in ("latexmk", "lualatex", "luahbtex", "luatex"):
        if shutil.which(name):
            (bin_dir / name).symlink_to(shutil.which(name))
    # Fake tlmgr: "installing" hb-missing provides hbmissing.sty in TEXMFHOME
    (bin_dir / "tlmgr").write_text(
        "#!/bin/sh\n"
        'case "$1" in\n'
        '  search) printf "hb-missing:\\n\\ttexmf-dist/tex/latex/hb-missing/hbmissing.sty\\n" ;;\n'
        '  install) mkdir -p "$TEXMFHOME/tex/latex" && echo "\\\\ProvidesPackage{hbmissing}" > "$TEXMFHOME/tex/latex/hbmissing.sty" ;;\n'
        "esac\n"
    )
    (bin_dir / "tlmgr").chmod(0o755)
    monkeypatch.setenv(tinytex.ENV_TINYTEX_DIR, str(root))

    tex = tmp_path / "doc" / "doc.tex"
    tex.parent.mkdir()
    tex.write_text("\\documentclass{article}\\usepackage{hbmissing}\\begin{document}x\\end{document}\n")

    result = cli_runner.invoke(app, ["tools", "latex", "doctor", str(tex)])
    assert result.exit_code == 1
    assert "Missing 'hbmissing.sty', provided by: hb-missing" in result.output

    result = cli_runner.invoke(app, ["tools", "latex", "doctor", "--fix", str(tex)])
    assert result.exit_code == 0, result.output
    assert "hb-missing" in json.loads((root / tinytex.MARKER_FILE).read_text())["packages"]


@pytest.mark.skipif(
    sys.platform == "win32" or not (shutil.which("latexmk") and shutil.which("lualatex")),
    reason="needs a TeX distribution on PATH",
)
def test_probe_compiles(tmp_path):
    import subprocess

    tex = tinytex.write_probe(tmp_path)
    result = subprocess.run(
        ["latexmk", "-pdf", "-pdflatex=lualatex", "-halt-on-error", "-interaction=nonstopmode", tex.name],
        cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True,
    )
    assert result.returncode == 0, (tmp_path / "probe.log").read_text(errors="replace")[-3000:]
