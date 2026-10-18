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

"""hb-managed LaTeX distribution based on TinyTeX (https://yihui.org/tinytex/).

TinyTeX is a relocatable TeX Live, so the very same installation procedure
works on Windows, Linux and macOS without admin rights. It lives in a
per-user directory owned by hermesbaby and is never added to the user's
global PATH; `hb pdf` puts it on the PATH of the build process only.

TeX Live never installs packages on the fly, so builds can not stop and
prompt. Everything a build needs is installed up front from packages.txt.
"""

import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Callable, Dict, List, Optional

TINYTEX_RELEASES_URL = "https://github.com/rstudio/tinytex-releases/releases/download"
TINYTEX_BUNDLE = "TinyTeX-1"

ENV_TINYTEX_DIR = "HERMESBABY_TINYTEX_DIR"
ENV_TINYTEX_VERSION = "HERMESBABY_TINYTEX_VERSION"

MARKER_FILE = "hermesbaby-tinytex.json"

# Fonts used for PDF builds on every platform. Referenced by file name so
# they resolve from the TeX tree (TinyTeX: package "dejavu") as well as from
# system font directories (CI: Debian package "fonts-dejavu").
LATEX_FONTPKG = r"""
\setmainfont{DejaVuSans}[
  Extension      = .ttf,
  UprightFont    = *,
  BoldFont       = *-Bold,
  ItalicFont     = *-Oblique,
  BoldItalicFont = *-BoldOblique
]
\setsansfont{DejaVuSans}[
  Extension      = .ttf,
  UprightFont    = *,
  BoldFont       = *-Bold,
  ItalicFont     = *-Oblique,
  BoldItalicFont = *-BoldOblique
]
\setmonofont{DejaVuSansMono}[
  Extension      = .ttf,
  UprightFont    = *,
  BoldFont       = *-Bold,
  ItalicFont     = *-Oblique,
  BoldItalicFont = *-BoldOblique,
  Scale          = 0.9
]
"""

# (pattern, suffix appended to the match if it lacks one)
_MISSING_FILE_PATTERNS = [
    (re.compile(r"! LaTeX Error: File `([^']+)' not found"), ""),
    (re.compile(r"! I can't find file `([^']+)'"), ""),
    (re.compile(r"Package fontspec Error:\s*The font \"([^\"]+)\" cannot be found"), ""),
    (re.compile(r"module '([^']+)' not found"), ".lua"),
]

Echo = Callable[[str], None]


class TinyTexError(Exception):
    pass


def root_dir() -> Path:
    """Directory of the hb-managed TinyTeX installation.

    The default avoids spaces in the path, which TeX tools handle poorly.
    """
    override = os.environ.get(ENV_TINYTEX_DIR)
    if override:
        return Path(override).expanduser()

    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return base / "hermesbaby" / "TinyTeX"
    if system == "Darwin":
        return Path.home() / "Library" / "hermesbaby" / "TinyTeX"
    base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "hermesbaby" / "TinyTeX"


def download_url(version: Optional[str] = None, system: Optional[str] = None, machine: Optional[str] = None) -> str:
    """URL of the TinyTeX bundle for the given (or current) platform.

    Without a version the "daily" build is used, which tracks the current
    TeX Live release.
    """
    if version is None:
        version = os.environ.get(ENV_TINYTEX_VERSION) or None
    system = system or platform.system()
    machine = (machine or platform.machine()).lower()

    if system == "Windows":
        extension = ".zip"
    elif system == "Darwin":
        extension = ".tgz"
    elif system == "Linux" and machine in ("x86_64", "amd64"):
        extension = ".tar.gz"
    else:
        raise TinyTexError(
            f"TinyTeX provides no prebuilt bundle for {system}/{machine}."
        )

    if version:
        version = version.lstrip("v")
        return f"{TINYTEX_RELEASES_URL}/v{version}/{TINYTEX_BUNDLE}-v{version}{extension}"
    return f"{TINYTEX_RELEASES_URL}/daily/{TINYTEX_BUNDLE}{extension}"


def bin_dir(root: Optional[Path] = None) -> Optional[Path]:
    """Platform bin directory of the installation (e.g. bin/x86_64-linux), if any."""
    root = root or root_dir()
    bin_root = root / "bin"
    if not bin_root.is_dir():
        return None
    for candidate in sorted(bin_root.iterdir()):
        if (candidate / "tlmgr").exists() or (candidate / "tlmgr.bat").exists():
            return candidate
    return None


def is_installed(root: Optional[Path] = None) -> bool:
    return bin_dir(root) is not None


def tool(name: str, root: Optional[Path] = None) -> Path:
    """Path of an executable in the installation, e.g. tool("tlmgr")."""
    directory = bin_dir(root)
    if directory is None:
        raise TinyTexError("TinyTeX is not installed. Run: hb tools latex install")
    for suffix in ("", ".exe", ".bat"):
        candidate = directory / f"{name}{suffix}"
        if candidate.exists():
            return candidate
    raise TinyTexError(f"'{name}' not found in {directory}")


def required_packages() -> List[str]:
    text = (Path(__file__).parent / "packages.txt").read_text(encoding="utf-8")
    packages = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            packages.append(line)
    return packages


def build_env(base_env: Optional[Dict[str, str]] = None, root: Optional[Path] = None) -> Dict[str, str]:
    """Environment for running the TeX tools of the installation.

    Puts the installation first on PATH and keeps per-user TeX trees
    (font cache, user formats, configuration) inside the installation so
    that a user's own LaTeX setup can neither interfere nor be modified.
    """
    root = root or root_dir()
    env = dict(os.environ if base_env is None else base_env)
    directory = bin_dir(root)
    if directory is None:
        raise TinyTexError("TinyTeX is not installed. Run: hb tools latex install")
    env["PATH"] = str(directory) + os.pathsep + env.get("PATH", "")
    env["TEXMFHOME"] = str(root / "texmf-home")
    env["TEXMFVAR"] = str(root / "texmf-var")
    env["TEXMFCONFIG"] = str(root / "texmf-config")
    return env


def read_marker(root: Optional[Path] = None) -> Optional[dict]:
    marker = (root or root_dir()) / MARKER_FILE
    try:
        return json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def missing_packages(root: Optional[Path] = None) -> List[str]:
    """Packages of packages.txt not installed by a previous `install`."""
    marker = read_marker(root) or {}
    installed = set(marker.get("packages", []))
    return [p for p in required_packages() if p not in installed]


def _path_warning(root: Path) -> Optional[str]:
    text = str(root)
    if " " in text or not text.isascii():
        return (
            f"Warning: the installation path '{text}' contains spaces or non-ASCII "
            f"characters, which some TeX tools can't handle. Set {ENV_TINYTEX_DIR} "
            f"to a plain path like C:\\TinyTeX or ~/TinyTeX."
        )
    return None


def _run(command: List[str], env: Dict[str, str], echo: Echo, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    echo(" ".join(str(c) for c in command))
    result = subprocess.run(
        [str(c) for c in command],
        env=env,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result


def _download(url: str, target: Path, echo: Echo) -> None:
    import requests

    echo(f"Downloading {url}")
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length") or 0)
        done = 0
        next_report = 0.1
        with open(target, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                done += len(chunk)
                if total and done / total >= next_report:
                    echo(f"  {done // (1024 * 1024)} / {total // (1024 * 1024)} MB")
                    next_report += 0.1


def _extract(archive: Path, target_dir: Path) -> None:
    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            z.extractall(target_dir)
    else:
        with tarfile.open(archive) as t:
            t.extractall(target_dir, filter="data")


def _make_writable_and_retry(func, path, _exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _rmtree(path: Path) -> None:
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_make_writable_and_retry)
    else:  # pragma: no cover
        shutil.rmtree(path, onerror=_make_writable_and_retry)


def _unpack_bundle(root: Path, version: Optional[str], echo: Echo) -> None:
    url = download_url(version)
    root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root.parent, prefix=".tinytex-") as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / url.rsplit("/", 1)[-1]
        _download(url, archive, echo)

        echo(f"Unpacking to {root}")
        staging = tmp_path / "staging"
        _extract(archive, staging)

        # The bundles contain a single top-level directory
        # (".TinyTeX" on Linux, "TinyTeX" on Windows and macOS)
        entries = list(staging.iterdir())
        if len(entries) != 1 or not entries[0].is_dir():
            raise TinyTexError(f"Unexpected layout of {archive.name}: {[e.name for e in entries]}")
        if root.exists():
            _rmtree(root)
        shutil.move(str(entries[0]), str(root))

    if not is_installed(root):
        raise TinyTexError(f"Unpacked TinyTeX at {root}, but found no bin directory with tlmgr")


def install_packages(packages: List[str], root: Optional[Path] = None, echo: Echo = print) -> None:
    root = root or root_dir()
    env = build_env(root=root)
    tlmgr = tool("tlmgr", root)

    # An older bundle's tlmgr refuses to work against a newer repository
    result = _run([tlmgr, "update", "--self"], env, echo)
    if result.returncode != 0:
        echo(result.stdout)
        raise TinyTexError("tlmgr update --self failed")

    result = _run([tlmgr, "install", *packages], env, echo)
    echo(result.stdout)
    if result.returncode != 0:
        raise TinyTexError("tlmgr install failed")


def warm_font_cache(root: Optional[Path] = None, echo: Echo = print) -> None:
    """Build the luaotfload font database now, not during the first PDF build."""
    root = root or root_dir()
    result = _run([tool("luaotfload-tool", root), "--update"], build_env(root=root), echo)
    if result.returncode != 0:
        echo(result.stdout)
        raise TinyTexError("luaotfload-tool --update failed")


def install(force: bool = False, version: Optional[str] = None, echo: Echo = print) -> Path:
    """Install TinyTeX (unless present) plus all packages of packages.txt.

    Running it again is cheap and brings an existing installation up to
    date with packages.txt.
    """
    root = root_dir()
    warning = _path_warning(root)
    if warning:
        echo(warning)

    if force or not is_installed(root):
        _unpack_bundle(root, version, echo)
    else:
        echo(f"TinyTeX already present at {root}")

    packages = required_packages()
    install_packages(packages, root, echo)
    warm_font_cache(root, echo)

    marker = {
        "tinytex_bundle": TINYTEX_BUNDLE,
        "tinytex_version": version or os.environ.get(ENV_TINYTEX_VERSION) or "daily",
        "packages": sorted(set(packages) | set((read_marker(root) or {}).get("packages", []))),
    }
    (root / MARKER_FILE).write_text(json.dumps(marker, indent=2), encoding="utf-8")
    return root


def update(echo: Echo = print) -> None:
    root = root_dir()
    result = _run([tool("tlmgr", root), "update", "--self", "--all"], build_env(root=root), echo)
    echo(result.stdout)
    if result.returncode != 0:
        raise TinyTexError(
            "tlmgr update failed. After a new yearly TeX Live release, "
            "reinstall with: hb tools latex install --force"
        )
    warm_font_cache(root, echo)


def uninstall(echo: Echo = print) -> None:
    root = root_dir()
    if not root.exists():
        echo(f"Nothing to do, {root} does not exist")
        return
    echo(f"Removing {root}")
    _rmtree(root)


def missing_files_from_log(log_text: str) -> List[str]:
    """Names of files (or fonts) a LaTeX run reported as missing."""
    found = []
    for pattern, suffix in _MISSING_FILE_PATTERNS:
        for match in pattern.finditer(log_text):
            name = match.group(1)
            if suffix and not name.endswith(suffix):
                name += suffix
            if name not in found:
                found.append(name)
    return found


def parse_tlmgr_file_search(output: str, file_name: str) -> List[str]:
    """Packages from `tlmgr search --global --file` output that ship exactly file_name."""
    packages = []
    current = None
    for line in output.splitlines():
        if line and not line[0].isspace() and line.rstrip().endswith(":"):
            current = line.rstrip()[:-1]
        elif current and line[:1].isspace():
            path = line.strip()
            if (path == file_name or path.endswith("/" + file_name)) and current not in packages:
                packages.append(current)
    return packages


def packages_providing(file_name: str, root: Optional[Path] = None, echo: Echo = print) -> List[str]:
    root = root or root_dir()
    result = _run(
        [tool("tlmgr", root), "search", "--global", "--file", "/" + file_name],
        build_env(root=root),
        echo,
    )
    return parse_tlmgr_file_search(result.stdout, file_name)


def probe_document() -> str:
    """A small document using the same packages and fonts as a Sphinx PDF build."""
    return (
        r"""\def\sphinxdocclass{report}
\documentclass[a4paper,10pt,english]{sphinxmanual}
\usepackage{fontspec}
\usepackage{amsmath,amssymb,amstext}
\usepackage[provide=*]{babel}
\babelprovide[main]{english}
"""
        + LATEX_FONTPKG
        + r"""
\usepackage[Bjarne]{fncychap}
\usepackage{sphinx}
\usepackage{geometry}
\usepackage{setspace}
\usepackage{graphicx}
\usepackage{adjustbox}
\usepackage{hyperref}
\usepackage{hypcap}
\makeindex
\begin{document}
\chapter{Probe}
Regular, \textbf{bold}, \textit{italic}, \textbf{\textit{bold italic}},
\texttt{monospace}, \textsf{sans}. Umlauts: äöüß.
\index{probe}
\begin{sphinxadmonition}{note}{Note:}
Admonition.
\end{sphinxadmonition}
\begin{sphinxVerbatim}
code block
\end{sphinxVerbatim}
\printindex
\end{document}
"""
    )


def write_probe(work_dir: Path) -> Path:
    """Write the probe document plus the support files Sphinx would put next to it."""
    import sphinx
    from sphinx.highlighting import PygmentsBridge

    for f in (Path(sphinx.__file__).parent / "texinputs").iterdir():
        if f.suffix in (".sty", ".cls", ".def", ".ist"):
            shutil.copy(f, work_dir / f.name)
    (work_dir / "sphinxhighlight.sty").write_text(
        "\\NeedsTeXFormat{LaTeX2e}[1995/12/01]\n"
        "\\ProvidesPackage{sphinxhighlight}\n"
        + PygmentsBridge("latex", "sphinx").get_stylesheet(),
        encoding="utf-8",
    )
    tex_file = work_dir / "probe.tex"
    tex_file.write_text(probe_document(), encoding="utf-8")
    return tex_file


def compile_tex(tex_file: Path, root: Optional[Path] = None, echo: Echo = print) -> subprocess.CompletedProcess:
    """Compile tex_file like `hb pdf` does (LuaLaTeX via latexmk, no prompting)."""
    root = root or root_dir()
    command = [
        tool("latexmk", root),
        # Rerun even if latexmk remembers a failure from a previous run,
        # which it does not invalidate when a missing package got installed
        "-g",
        "-pdf",
        "-pdflatex=lualatex",
        "-halt-on-error",
        "-file-line-error",
        "-interaction=nonstopmode",
        "-latexoption=-interaction=nonstopmode",
        tex_file.name,
    ]
    return _run(command, build_env(root=root), echo, cwd=tex_file.parent)


def doctor(tex_file: Optional[Path] = None, fix: bool = False, echo: Echo = print, max_rounds: int = 10) -> bool:
    """Compile tex_file (default: the probe document) and resolve missing packages.

    Returns True when the document compiles.
    """
    root = root_dir()
    with tempfile.TemporaryDirectory(prefix="hb-latex-doctor-") as tmp:
        if tex_file is None:
            tex_file = write_probe(Path(tmp))
        else:
            tex_file = tex_file.resolve()

        attempted = set()
        for _ in range(max_rounds):
            result = compile_tex(tex_file, root, echo)
            if result.returncode == 0:
                echo(f"OK: {tex_file.name} compiles.")
                return True

            log_file = tex_file.with_suffix(".log")
            log_text = result.stdout
            if log_file.exists():
                log_text += log_file.read_text(encoding="utf-8", errors="replace")

            missing = [m for m in missing_files_from_log(log_text) if m not in attempted]
            if not missing:
                echo(result.stdout[-3000:])
                echo(f"FAILED: {tex_file.name} does not compile, and no missing file was detected (see {log_file}).")
                return False

            to_install = []
            for name in missing:
                attempted.add(name)
                providers = packages_providing(name, root, echo) if "." in name else []
                if providers:
                    echo(f"Missing '{name}', provided by: {', '.join(providers)}")
                    to_install.append(providers[0])
                else:
                    echo(f"Missing '{name}', no TeX Live package found providing it.")

            if not fix or not to_install:
                if to_install:
                    echo("Run again with --fix to install them, and add them to packages.txt.")
                return False

            install_packages(to_install, root, echo)
            marker = read_marker(root) or {}
            marker["packages"] = sorted(set(marker.get("packages", [])) | set(to_install))
            (root / MARKER_FILE).write_text(json.dumps(marker, indent=2), encoding="utf-8")

        echo("Giving up after too many rounds.")
        return False
