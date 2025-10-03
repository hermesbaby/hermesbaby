# -*- mode: python ; coding: utf-8 -*-

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

import sys
import shutil
from pathlib import Path
import tomllib
from PyInstaller.utils.hooks import collect_all, collect_submodules

# --- Project paths ------------------------------------------------
project_root = Path(sys.argv[0]).resolve().parent
src_dir = project_root / "src"
hermesbaby_dir = src_dir / "hermesbaby"

# --- Read pyproject.toml ------------------------------------------
pyproject = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))

# Runtime dependencies (ignore Python itself)
dependencies = pyproject["tool"]["poetry"]["dependencies"]
packages_to_collect = [pkg for pkg in dependencies.keys() if pkg.lower() != "python"]

# Also include dev dependencies if desired
dev_deps = (
    pyproject.get("tool", {})
             .get("poetry", {})
             .get("group", {})
             .get("dev", {})
             .get("dependencies", {})
)
packages_to_collect += list(dev_deps.keys())

# Add your own package explicitly
packages_to_collect.append("hermesbaby")

# --- Collect package files ----------------------------------------
datas, binaries, hiddenimports = [], [], []

for pkg in packages_to_collect:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception as e:
        print(f"[WARN] Skipping {pkg}: {e}")

# Always brute-force your own submodules
hiddenimports += collect_submodules("hermesbaby")

# --- Explicit HermesBaby resources --------------------------------
extra_datas = [
    (str(hermesbaby_dir / "templates"), "hermesbaby/templates"),
    (str(hermesbaby_dir / "external_tools.json"), "hermesbaby"),
    (str(hermesbaby_dir / "vscode-extensions"), "hermesbaby/vscode-extensions"),
    (str(hermesbaby_dir / "htaccess.yaml"), "hermesbaby"),
    (str(hermesbaby_dir / "Kconfig"), "hermesbaby"),
    (str(hermesbaby_dir / "Makefile"), "hermesbaby"),
    (str(hermesbaby_dir / "tools"), "hermesbaby/tools"),
    (str(hermesbaby_dir / "plantuml.config"), "hermesbaby"),
    (str(hermesbaby_dir / "puppeteer.config.json"), "hermesbaby"),
    (str(hermesbaby_dir / "scoopfile-build.json"), "hermesbaby"),
    (str(hermesbaby_dir / "html_static"), "hermesbaby/html_static"),
    (str(hermesbaby_dir / "setup.sh"), "hermesbaby"),
    (str(hermesbaby_dir / "setup.cmd"), "hermesbaby"),
    (str(hermesbaby_dir / "setup.ps1"), "hermesbaby"),
]
datas += extra_datas

# --- Add executables explicitly used by HermesBaby ----------------
scripts_dir = Path(sys.executable).parent
entry_points = ["sphinx-build", "sphinx-apidoc", "sphinx-autobuild", "guiconfig", "menuconfig"]

for ep in entry_points:
    exe_file = scripts_dir / (ep + (".exe" if sys.platform.startswith("win") else ""))
    if exe_file.exists():
        binaries.append((str(exe_file), "."))  # will land in _internal
        print(f"[INFO] Bundled entry point (goes to _internal first): {exe_file}")
    else:
        print(f"[WARN] Entry point not found: {ep}")

# --- Analysis -----------------------------------------------------
a = Analysis(
    [str(hermesbaby_dir / "__main__.py")],
    pathex=[str(src_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="hb",
    console=True,
    icon="hermesbaby.ico" if sys.platform.startswith("win") else None,
)

# --- Dir-bundle distribution (onedir) -----------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True if sys.platform.startswith("win") else False,
    upx_exclude=[],
    name="hermesbaby",
)

# --- Post-process: copy entry point executables to dist root -------
dist_root = Path("dist") / "hermesbaby"
for ep in entry_points:
    exe_name = ep + (".exe" if sys.platform.startswith("win") else "")
    exe_src = scripts_dir / exe_name
    exe_dst = dist_root / exe_name
    if exe_src.exists():
        try:
            shutil.copy2(exe_src, exe_dst)
            print(f"[INFO] Copied {exe_name} into dist root")
        except Exception as e:
            print(f"[WARN] Could not copy {exe_name}: {e}")
