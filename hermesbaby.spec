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
import os
from pathlib import Path

# Get the source directory
src_dir = Path(os.getcwd()) / "src"
hermesbaby_dir = src_dir / "hermesbaby"

# Get cookiecutter package data
import cookiecutter
cookiecutter_path = Path(cookiecutter.__file__).parent

# Data files to include
datas = [
    # Templates directory
    (str(hermesbaby_dir / "templates"), "hermesbaby/templates"),
    # Configuration files
    (str(hermesbaby_dir / "external_tools.json"), "hermesbaby"),
    (str(hermesbaby_dir / "extensions.json"), "hermesbaby"),
    (str(hermesbaby_dir / "htaccess.yaml"), "hermesbaby"),
    (str(hermesbaby_dir / "Kconfig"), "hermesbaby"),
    (str(hermesbaby_dir / "Makefile"), "hermesbaby"),
    (str(hermesbaby_dir / "plantuml.config"), "hermesbaby"),
    (str(hermesbaby_dir / "puppeteer.config.json"), "hermesbaby"),
    (str(hermesbaby_dir / "scoopfile-build.json"), "hermesbaby"),
    # Static files
    (str(hermesbaby_dir / "html_static"), "hermesbaby/html_static"),
    # Setup scripts
    (str(hermesbaby_dir / "setup.sh"), "hermesbaby"),
    (str(hermesbaby_dir / "setup.cmd"), "hermesbaby"),
    (str(hermesbaby_dir / "setup.ps1"), "hermesbaby"),
    # Tools directory (if exists)
    (str(hermesbaby_dir / "tools"), "hermesbaby/tools"),
    # Package subdirectories
    (str(hermesbaby_dir / "atlassian-admin"), "hermesbaby/atlassian-admin"),
    (str(hermesbaby_dir / "loflot"), "hermesbaby/loflot"),
    (str(hermesbaby_dir / "pre-post-build"), "hermesbaby/pre-post-build"),
    (str(hermesbaby_dir / "rst-frontmatter"), "hermesbaby/rst-frontmatter"),
    (str(hermesbaby_dir / "tag-anything"), "hermesbaby/tag-anything"),
    (str(hermesbaby_dir / "toctree-only"), "hermesbaby/toctree-only"),
    (str(hermesbaby_dir / "toolbox"), "hermesbaby/toolbox"),
    (str(hermesbaby_dir / "update"), "hermesbaby/update"),
    (str(hermesbaby_dir / "web_access_ctrl"), "hermesbaby/web_access_ctrl"),
    # Cookiecutter data files
    (str(cookiecutter_path / "VERSION.txt"), "cookiecutter"),
]

# Hidden imports - packages that might not be automatically detected
hiddenimports = [
    'hermesbaby',
    'hermesbaby.atlassian-admin',
    'hermesbaby.loflot',
    'hermesbaby.pre-post-build',
    'hermesbaby.rst-frontmatter',
    'hermesbaby.tag-anything',
    'hermesbaby.toctree-only',
    'hermesbaby.toolbox',
    'hermesbaby.update',
    'hermesbaby.web_access_ctrl',
    'typer',
    'kconfiglib',
    'cookiecutter',
    # Only include commonly used imports, others will be lazy loaded
    'requests',
    'urllib3',
    'sphinx',
]

# Analysis configuration
a = Analysis(
    [str(hermesbaby_dir / "__main__.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Only exclude clearly unused GUI packages
        'turtle', 'pydoc_data',
        # Exclude unused networking/crypto (if not needed)
        'ftplib', 'poplib', 'imaplib',
    ],
    noarchive=False,
    optimize=2,  # Enable Python optimization level 2
)

# Package configuration
pyz = PYZ(a.pure)

# Create COLLECT for one-directory mode (faster startup)
exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty - binaries and datas will be in COLLECT
    name='hermesbaby',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Enable stripping to reduce size
    upx=True,    # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# One-directory distribution for faster startup
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='hermesbaby'
)
